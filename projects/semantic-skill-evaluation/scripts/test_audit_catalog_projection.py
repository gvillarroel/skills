#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preservation, identity, ordered-value and fail-closed contract regressions."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).with_name("audit_catalog_projection.py")
spec=importlib.util.spec_from_file_location("catalog_audit",SCRIPT)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def raw(value):
    return json.dumps(value,ensure_ascii=False,indent=2).encode()

def fixture():
    return {"terms":[{"id":"urn:a","label":"Port","definition":"A facility.",
        "synonyms":["harbour","haven"],"certified":True,"pk":["tenant","id"]},
        {"id":"urn:b","label":"Port","definition":"A network endpoint.",
         "synonyms":["socket"],"certified":False}]}

def contract(source,projected):
    return {"schema_version":1,"source_records":"/terms","projected_records":"/terms",
        "source_sha256":{"source":sha256(source).hexdigest(),"projected":sha256(projected).hexdigest()},
        "fields":[{"name":f,"source":"/"+f,"projected":"/"+f,
            "mode":"unordered" if f=="synonyms" else "ordered",
            "category":"review" if f=="certified" else "semantic"}
            for f in ("label","definition","synonyms","certified","pk")]}

class ProjectionTests(unittest.TestCase):
    def compare(self,source=None,projected=None,mutate_contract=None):
        source=fixture() if source is None else source
        projected=deepcopy(source) if projected is None else projected
        a,b=raw(source),raw(projected);c=contract(a,b)
        if mutate_contract: mutate_contract(c)
        return audit.audit(a,b,raw(c))

    def test_equal_declared_fields(self):
        r,code=self.compare();self.assertEqual(code,0);self.assertEqual(r["counts"]["preserved_fields"],9)

    def test_record_order_invariant(self):
        a=fixture();b=deepcopy(a);b["terms"].reverse()
        r,code=self.compare(a,b);self.assertEqual(code,0);self.assertEqual(*r["fingerprints"].values())

    def test_object_key_order_invariant(self):
        a=fixture();b={key:value for key,value in reversed(list(a.items()))}
        for i,row in enumerate(b["terms"]): b["terms"][i]=dict(reversed(list(row.items())))
        self.assertEqual(self.compare(a,b)[1],0)

    def test_declared_alias_set_order(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["synonyms"].reverse()
        self.assertEqual(self.compare(a,b)[1],0)

    def test_ordered_composite_key_changes(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["pk"].reverse()
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertEqual(r["field_changes"][0]["field"],"pk")

    def test_duplicate_alias_multiplicity(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["synonyms"].append("harbour")
        self.assertEqual(self.compare(a,b)[1],1)

    def test_native_projection_loss_fields(self):
        a=fixture();b=deepcopy(a)
        for field in ("synonyms","certified"): del b["terms"][0][field]
        r,code=self.compare(a,b);self.assertEqual(code,1)
        self.assertEqual({row["field"] for row in r["field_changes"]},{"synonyms","certified"})
        self.assertEqual({row["status"] for row in r["field_changes"]},{"lost-field"})

    def test_missing_is_distinct_from_null(self):
        a=fixture();a["terms"][0]["definition"]=None;b=deepcopy(a);del b["terms"][0]["definition"]
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertIsNone(r["field_changes"][0]["before"])

    def test_review_category_preserved(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["certified"]=False
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertEqual(r["field_changes"][0]["category"],"review")

    def test_boolean_is_not_number(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["certified"]=1
        self.assertEqual(self.compare(a,b)[1],1)

    def test_review_change_does_not_change_semantic_field_view(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["certified"]=False
        r,code=self.compare(a,b);self.assertEqual(code,1)
        self.assertEqual(r["category_fingerprints"]["semantic"]["status"],"preserved")
        self.assertEqual(r["category_fingerprints"]["review"]["status"],"differences")
        self.assertEqual(r["semantic_status"],"not_checked")

    def test_provenance_change_has_separate_view(self):
        a=fixture();b=deepcopy(a)
        a["terms"][0]["locator"]="old.txt#L1";b["terms"][0]["locator"]="new.txt#L2"
        r,code=self.compare(a,b,lambda c:c["fields"].append({"name":"locator","source":"/locator","projected":"/locator","category":"provenance"}))
        self.assertEqual(code,1)
        self.assertEqual(r["category_fingerprints"]["semantic"]["status"],"preserved")
        self.assertEqual(r["category_fingerprints"]["provenance"]["status"],"differences")

    def test_definition_change_has_semantic_field_difference(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["definition"]="A regulated facility."
        r,code=self.compare(a,b);self.assertEqual(code,1)
        self.assertEqual(r["category_fingerprints"]["semantic"]["status"],"differences")
        self.assertEqual(r["category_fingerprints"]["review"]["status"],"preserved")

    def test_unselected_category_has_no_preservation_claim(self):
        r,_=self.compare()
        self.assertEqual(r["category_fingerprints"]["provenance"],{"fields":[],"status":"not_selected","source":None,"projected":None})

    def test_absent_category_fields_remain_unchecked(self):
        r,_=self.compare(mutate_contract=lambda c:c["fields"].append({"name":"locator","source":"/locator","projected":"/locator","category":"provenance"}))
        self.assertEqual(r["category_fingerprints"]["provenance"]["status"],"not_checked")

    def test_category_views_use_reviewed_identity_bridge(self):
        a=fixture();b=deepcopy(a)
        b["terms"][0]["id"]="local-a";b["terms"][1]["id"]="local-b"
        r,_=self.compare(a,b,lambda c:c.update(bindings={"projected":{"local-a":"urn:a","local-b":"urn:b"}}))
        for category in ("semantic","review"):
            view=r["category_fingerprints"][category]
            self.assertEqual(view["source"],view["projected"])

    def test_scalar_type_change(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["definition"]=17
        self.assertEqual(self.compare(a,b)[1],1)

    def test_homonyms_remain_distinct(self):
        a=fixture();b=deepcopy(a);b["terms"][1]["definition"]="A software endpoint."
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertEqual(r["field_changes"][0]["id"],"urn:b")

    def test_explicit_local_identity_bridge(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["id"]="local-9";b["terms"][1]["id"]="local-4"
        r,code=self.compare(a,b,lambda c:c.update(bindings={"projected":{"local-9":"urn:a","local-4":"urn:b"}}))
        self.assertEqual(code,0);self.assertEqual(*r["fingerprints"].values())

    def test_unbound_local_identity_not_inferred(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["id"]="fresh"
        r,code=self.compare(a,b);self.assertEqual(code,1)
        self.assertEqual({v["status"] for v in r["record_changes"]},{"lost-record","introduced-record"})

    def test_distinct_identity_field_paths(self):
        a=fixture();b=deepcopy(a)
        for row in b["terms"]: row["local_key"]=row.pop("id")
        r,code=self.compare(a,b,lambda c:c.update(projected_id_path="/local_key"))
        self.assertEqual(code,0);self.assertEqual(*r["fingerprints"].values())

    def test_nested_per_side_identity_bridge(self):
        a=fixture();b=deepcopy(a)
        for row in a["terms"]: row["identity"]={"key":row.pop("id")}
        for index,row in enumerate(b["terms"]):
            row.pop("id");row["native"]={"key":"local-"+str(index)}
        r,code=self.compare(a,b,lambda c:c.update(source_id_path="/identity/key",projected_id_path="/native/key",
            bindings={"projected":{"local-0":"urn:a","local-1":"urn:b"}}))
        self.assertEqual(code,0);self.assertEqual(*r["fingerprints"].values())

    def test_shared_id_path_remains_a_fallback(self):
        a=fixture();b=deepcopy(a)
        for row in a["terms"]: row["key"]=row.pop("id")
        for row in b["terms"]: row["local_key"]=row.pop("id")
        self.assertEqual(self.compare(a,b,lambda c:c.update(id_path="/key",projected_id_path="/local_key"))[1],0)

    def test_explicit_side_path_does_not_guess(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(source_id_path="/absent"))

    def test_invalid_side_identity_path_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(projected_id_path="local_key"))

    def test_partial_bridge_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(bindings={"projected":{"urn:a":"urn:a"}}))

    def test_merging_bridge_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(bindings={"projected":{"urn:a":"one","urn:b":"one"}}))

    def test_null_bridge_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(bindings={"source":None}))

    def test_duplicate_ids_rejected(self):
        a=fixture();a["terms"][1]["id"]="urn:a"
        with self.assertRaises(audit.ContractError): self.compare(a)

    def test_missing_record(self):
        a=fixture();b=deepcopy(a);b["terms"].pop()
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertEqual(r["record_changes"],[{"id":"urn:b","status":"lost-record"}])

    def test_dictionary_record_keys(self):
        a=fixture();b=deepcopy(a)
        a={"terms":{row["id"]:row for row in a["terms"]}}
        self.assertEqual(self.compare(a,b)[1],0)

    def test_empty_authority_not_a_pass(self):
        with self.assertRaises(audit.ContractError): self.compare({"terms":[]})

    def test_explicit_empty_authority(self):
        r,code=self.compare({"terms":[]},mutate_contract=lambda c:c.update(allow_empty_source=True))
        self.assertEqual(code,0);self.assertEqual(r["counts"]["authoritative_fields_checked"],0)

    def test_empty_record_presence_changes_fingerprint(self):
        a={"terms":[]};b={"terms":[{"id":"empty"}]}
        r,code=self.compare(a,b,lambda c:c.update(allow_empty_source=True))
        self.assertEqual(code,1);self.assertNotEqual(*r["fingerprints"].values())

    def test_scope_is_explicit(self):
        a=fixture();b=deepcopy(a);b["terms"][0]["unselected_field"]="extra"
        r,code=self.compare(a,b);self.assertEqual(code,0);self.assertEqual(r["semantic_status"],"not_checked")
        self.assertNotIn("unselected_field",r["field_scope"])

    def test_no_selected_source_fields_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare({"terms":[{"id":"empty"}]})

    def test_added_selected_field_visible(self):
        a=fixture();b=deepcopy(a);b["terms"][1]["pk"]=["id"]
        r,code=self.compare(a,b);self.assertEqual(code,1);self.assertEqual(r["field_changes"][0]["status"],"introduced-field")

    def test_bad_pointer_escape_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c.update(source_records="/bad~2path"))

    def test_pointer_escape_roundtrip(self):
        self.assertEqual(audit.lookup({"a/b":{"~x":5}},"/a~1b/~0x"),5)

    def test_array_pointer_index_policy(self):
        with self.assertRaises(audit.ContractError): audit.lookup([3],"/00")

    def test_duplicate_contract_field_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c["fields"].append(deepcopy(c["fields"][0])))

    def test_stale_source_hash_rejected(self):
        with self.assertRaises(audit.ContractError):
            self.compare(mutate_contract=lambda c:c["source_sha256"].update(source="0"*64))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(audit.ContractError): audit.decode(b'{"id":1,"id":2}')

    def test_nonfinite_numbers_rejected(self):
        for text in (b'{"n":NaN}',b'{"n":Infinity}',b'{"n":1e999}'):
            with self.subTest(text=text), self.assertRaises(audit.ContractError): audit.decode(text)

    def test_decimal_precision_loss_rejected(self):
        with self.assertRaises(audit.ContractError): audit.decode(b'{"n":0.1234567890123456789}')

    def test_safe_decimal_roundtrip(self):
        self.assertEqual(audit.encode(audit.decode(b'{"n":0.1}')),'{"n":0.1}')

    def test_unordered_field_type_rejected(self):
        a=fixture();a["terms"][0]["synonyms"]="harbour"
        with self.assertRaises(audit.ContractError): self.compare(a)

    def test_cli_reports_are_reproducible_and_exclusive(self):
        with tempfile.TemporaryDirectory(prefix=".projection-test-",dir=Path.cwd()) as temporary:
            root=Path(temporary).resolve();self.assertTrue(root.is_relative_to(Path.cwd().resolve()))
            a=raw(fixture()); b=a; c=raw(contract(a,b))
            for name,data in (("source.json",a),("projected.json",b),("contract.json",c)): (root/name).write_bytes(data)
            command=[sys.executable,str(SCRIPT),"--source",str(root/"source.json"),"--projected",str(root/"projected.json"),"--contract",str(root/"contract.json"),"--report"]
            one=subprocess.run(command+[str(root/"one.json")],capture_output=True)
            two=subprocess.run(command+[str(root/"two.json")],capture_output=True)
            self.assertEqual((one.returncode,two.returncode),(0,0))
            self.assertEqual((root/"one.json").read_bytes(),(root/"two.json").read_bytes())
            again=subprocess.run(command+[str(root/"one.json")],capture_output=True)
            self.assertEqual(again.returncode,2)

    def test_cli_cannot_replace_input(self):
        with tempfile.TemporaryDirectory(prefix=".projection-test-",dir=Path.cwd()) as temporary:
            root=Path(temporary);a=raw(fixture());c=raw(contract(a,a))
            for name,data in (("source.json",a),("projected.json",a),("contract.json",c)): (root/name).write_bytes(data)
            result=subprocess.run([sys.executable,str(SCRIPT),"--source",str(root/"source.json"),
              "--projected",str(root/"projected.json"),"--contract",str(root/"contract.json"),
              "--report",str(root/"source.json")],capture_output=True)
            self.assertEqual(result.returncode,2);self.assertEqual((root/"source.json").read_bytes(),a)

if __name__=="__main__":
    unittest.main()
