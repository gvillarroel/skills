#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare semantic narration cues for the requested visual revision."""
import json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
def cue(target,phrase,**extra):return dict(target=target,phrase=phrase,**extra)
spec={'scenes':[
 {'id':'generalize','cues':[cue('samples','ejemplos'),cue('controlled-fit','datos nuevos'),cue('flexible-fit','demasiado flexible'),cue('controlled-fit','reducen ese riesgo')]},
 {'id':'problem-data','cues':[cue('objective','qué predecir'),cue('input','información disponible'),cue('error','error'),cue('provenance','procedencia'),cue('labels','etiquetas'),cue('missing','ausentes'),cue('duplicates','duplicados'),cue('coverage','representatividad'),cue('coverage','uso real')]},
 {'id':'split','cues':[cue('train-label','entrenamiento'),cue('validation-label','validación'),cue('test-label','prueba'),cue('split-train','sesenta'),cue('split-validation','veinte',occurrence=1),cue('split-test','veinte',occurrence=2),cue('grouped','misma entidad'),cue('sealed','prueba queda cerrado')]},
 {'id':'preprocessing','cues':[cue('impute','imputación'),cue('scale','escalado'),cue('select','selección de variables'),cue('fit-only','únicamente del entrenamiento'),cue('apply-only','aplicamos'),cue('apply-model','validación y prueba'),cue('fit-only','cada partición'),cue('no-refit','información reservada')]},
 {'id':'baseline','cues':[cue('baseline-bar','referencia sencilla'),cue('baseline-value','media'),cue('selected-bar','aumentamos la capacidad'),cue('cv-small','demasiado simple'),cue('cv-large','excesivamente complejo'),cue('cv-selected','comparamos'),cue('unseen','no utilizaron')]},
 {'id':'cross-validation','cues':[cue('folds','cinco'),cue('held-fold','reservada'),cue('cv-mean','error medio'),cue('cv-sd','variabilidad'),cue('selected-degree','alternativas'),cue('cv-mean','procedimiento de selección')]},
 {'id':'regularization','cues':[cue('large-coefficient','complejidad'),cue('penalty','penalización'),cue('small-coefficient','reduce',alternatives=['reduce coeficiente']),cue('penalty','conserven el significado')]},
 {'id':'early-stopping','cues':[cue('training-curve','entrenamiento'),cue('validation-curve','validación separada'),cue('best-state','deja de mejorar'),cue('restore','recuperamos'),cue('training-curve','entrenamiento sea perfecto'),cue('schematic','esquema')]},
 {'id':'diagnostics','cues':[cue('train-error','entrenamiento'),cue('cv-error','validación'),cue('more-data','aumentar los datos'),cue('cv-error','ambos conjuntos'),cue('error-gap','diferencia grande'),cue('group-cv','particiones apropiadas')]},
 {'id':'final-test','cues':[cue('frozen','Congelamos'),cue('hyperparameters','hiperparámetros'),cue('development','desarrollo'),cue('test-score','prueba final'),cue('test-score','resultado'),cue('uncertainty','incertidumbre'),cue('independent','evaluación independiente')]},
 {'id':'production','cues':[cue('versions','versiones'),cue('input-data','entradas'),cue('predictions','predicciones'),cue('real-error','error'),cue('input-data','distribución nueva'),cue('reevaluate','evaluación renovada')]},
 {'id':'overview','cues':[cue('world-data','datos adecuados'),cue('world-split','separación correcta'),cue('world-pipeline','sin fugas'),cue('world-capacity','capacidad controlada'),cue('world-validation','validación honesta'),cue('world-test','prueba independiente',alternatives=['prove independiente']),cue('world-production','producción'),cue('world-all','proceso reproducible'),cue('world-all','fuera del entrenamiento')]}
]}
out=ROOT/'artifacts/revision';out.mkdir(parents=True,exist_ok=True)
(out/'cue-spec.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
subprocess.run(['uv','run','--script',str(REPO/'skills/line-world-google-vids/scripts/narration_cues.py'),'--transcript',str(ROOT/'artifacts/reviews/narration-transcript.json'),'--timing',str(ROOT/'artifacts/handoff/timing.json'),'--spec',str(out/'cue-spec.json'),'--output',str(out/'cues.json')],check=True)

if __name__=='__main__':pass
