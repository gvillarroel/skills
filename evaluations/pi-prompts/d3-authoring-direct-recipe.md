Create a small offline animated explanation using the D3 speculative-decoding
recipe. The example is illustrative: after the prompt, a draft proposes the
tokens "the", "answer", "is", and "42". Verification accepts the first three,
rejects "42", and resumes with "next". Show the draft path, committed prefix,
rejected tail and the verification step so their roles remain understandable
without motion. Use colorset2 and a readable 720 by 440 canvas.

Save out/decode.html and a self-contained accessible out/decode.svg. Include
replay in the HTML, retain the final meaningful SVG state, validate the outputs,
and inspect them before finishing. The files are educational illustrations;
do not run an inference model or obtain external data.

The skill at skills/d3/ is read-only. Work only in this workspace, with no
network, package installation, acceptance examples, repository documentation,
or other skills.
