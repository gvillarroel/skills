# Rights and Provenance

Treat transformation rights as an input requirement, not a post-processing note. This workflow is conservative and is not a substitute for jurisdiction-specific legal advice.

## Accepted Inputs

- A user-owned or user-created image explicitly supplied for modification.
- Public-domain material with a source page that states its status.
- CC0 material.
- CC BY material when attribution is retained.
- CC BY-SA material when attribution and the applicable ShareAlike obligation are retained.

The downloader accepts only `Public-Domain`, `CC0`, `CC BY`, and `CC BY-SA` evidence that permits commercial reuse and derivative works.

## Reject by Default

- Any `NoDerivatives` or `ND` license.
- Any `NonCommercial` or `NC` restriction.
- Editorial-only, educational-only, or personal-use-only material.
- Fair-use copies, watermarked marketplace previews, or social-media reposts.
- A museum image whose page allows viewing but does not mark the image as Open Access.
- Missing, contradictory, or unverifiable license information.
- An open-license claim copied from a search snippet without checking the source file page.

Do not download first and investigate later. Resolve the source record and license before writing the asset.

## Supported Evidence Paths

### Wikimedia Commons

Use the `imageinfo` API with `url`, `extmetadata`, `sha1`, `mime`, and `size`. The bundled downloader checks `LicenseShortName`, `LicenseUrl`, `UsageTerms`, and `Restrictions`, then stores the exact file-page and metadata-API URLs.

Official references:

- MediaWiki `imageinfo`: <https://www.mediawiki.org/wiki/API:Imageinfo>
- Commons metadata fields: <https://www.mediawiki.org/wiki/Extension:CommonsMetadata>
- Commons reuse guidance: <https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/en>

### Art Institute of Chicago

Require `is_public_domain: true` and a nonempty `image_id` from the official API. Download through the returned IIIF base URL. The museum offers unrestricted CC0 use for its Open Access images.

- Open Access policy: <https://www.artic.edu/open-access>
- API and IIIF documentation: <https://api.artic.edu/docs/>

### Additional Providers

Use another provider only when its official object record or API exposes all of the following:

- creator and work title;
- source/object page;
- exact image or media record;
- license name and license URL;
- explicit permission for modification and commercial reuse;
- stable download URL;
- no conflicting restrictions.

Store the same fields as the bundled manifest before vectorization.

## Manifest Contract

Each downloaded source record must include:

- stable lowercase hyphen-case `id`;
- relative `filename`;
- provider and provider object ID;
- title, creator, and date;
- source page, metadata API URL, original URL, and actual download URL;
- retrieval timestamp;
- normalized license and license URL;
- attribution and ShareAlike flags;
- restrictions and `transformation_allowed: true`;
- decoded MIME type, dimensions, byte count, SHA-256, and provider hash when available.

The vectorizer verifies the input path and SHA-256 against this record. Do not edit a downloaded image in place; keep the verified base image immutable and write derivatives elsewhere.

## Attribution in Derivatives

- Keep provenance inside SVG `<metadata>` and in the JSON vectorization report.
- Credit public-domain works even when not legally required; it preserves the research trail.
- For CC BY, include the creator, title, source, license, and an indication that the SVG is modified.
- For CC BY-SA, also apply the required compatible license to the derivative before distribution.
- Do not imply that the source artist, museum, or uploader endorses the derivative.

Creative Commons distinguishes BY, ShareAlike, NonCommercial, and NoDerivatives conditions: <https://creativecommons.org/share-your-work/use-remix/cc-licenses/>.
