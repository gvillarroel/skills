# Standard Import API route

Checked 2026-10-07. Standard Import is a documented API format, not a generic SVG document converter or an assumed editor file-import option.

## Package and subset

The `.lucid` file is a ZIP with root `document.json`, Standard Import `version: 1`, and at least one page. Page and object IDs must be globally unique. Native shapes use a `type`, `boundingBox`, text, and style; native lines attach with `shapeEndpoint` objects. The bundled compiler implements only the subset in [native-reconstruction.md](native-reconstruction.md).

Official limits: ZIP contents 50 MB; `document.json` 2 MB; `data/` 1 MB; `images/` 50 MB. The compiler contains no image resources. If using Standard Import images separately, SVG image inputs are converted to PNG. This route cannot establish vector preservation for SVG artwork.

## Authentication and submission

Prefer an available authenticated Lucid connector when it explicitly supports Standard Import creation. Otherwise use an existing OAuth bearer access token with `lucidchart.document.content` or appropriate app-folder scope; the endpoint also documents API keys with DocumentEdit access. A normal signed-in editor session or MCP OAuth connection does not automatically supply a REST bearer token. Do not extract cookies or create credentials without user authorization.

Use the current endpoint reference before submission:

```text
POST https://api.lucid.co/v1/documents/create
Authorization: Bearer <existing authorized access token>
Lucid-Api-Version: 1
Content-Type: multipart/form-data; boundary=<client-generated boundary>

file: native.lucid bytes
type: x-application/vnd.lucid.standardImport
product: lucidchart
title: <requested title>              (optional)
parent: <authorized folder ID>        (optional)
```

Let the HTTP client form the multipart boundary. Supply `type` as its own form field and set the file part's media type to `x-application/vnd.lucid.standardImport`. Read the existing token through an environment/secret facility; never put it in source files, prompts, command-line literals, manifests, or logs. No token-management or upload script is bundled because browser/connector/HTTP capabilities differ between environments.

The older Standard Import overview example uses `POST /v1/documents`; the dedicated current endpoint reference uses `/v1/documents/create`. Prefer the endpoint reference and recheck it if requests fail; do not guess private routes.

Expect a 201 Document resource. Record its actual document ID and editor URL, then open that returned document to verify native content. A 400 indicates malformed input; inspect and repair locally. A 403 can indicate insufficient scope or folder access; a 415 indicates unsupported format. Do not repeatedly submit after a timeout: creation may have succeeded, so check the account/document list or available integration state before another POST. A package without successful authenticated submission is a prepared artifact, not a created Lucid document.

## Authoritative sources

- [Create from Standard Import File](https://developer.lucid.co/reference/createdocumentwithstandardimport)
- [Standard Import overview and limits](https://lucid.readme.io/docs/overview-si)
- [Shapes](https://developer.lucid.co/docs/shapes-si)
- [Standard shape library](https://developer.lucid.co/docs/standard-library-si)
- [Lines](https://developer.lucid.co/docs/lines-si)
- [Images](https://developer.lucid.co/docs/images-si)

Local validators check a documented subset. Lucid notes that an unchanged Standard Import package may produce different results as the service evolves; live parser/render acceptance remains a separate check.
