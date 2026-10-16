# fnMR · Qwen3.8-Flash-Next

**Functional neural MoE routing** — an interactive atlas of the experts selected while Nebula processed 1,800 questions across 12 domains.

## [Open Router Lab →](https://ivanpanzera.github.io/fnmr-qwen3.8-flash-next/)

Explore original token-level traces, question and domain averages, expert-weight filters, recorded timings, and train-only hotlist coverage. Questions and answers have English reading translations alongside the original text. The token view always shows the original stream used in the experiment.

## Download all the data

**All data displayed in Router Lab are publicly downloadable, including the complete routing trace for every recorded token.** Download both archives below for the full collection:

| Download | Size | Contents |
|---|---:|---|
| **[All token-level routing traces — ZIP](https://github.com/IvanPanzera/fnmr-qwen3.8-flash-next/releases/download/source-bundle-v1/fnmr-traces-v1.zip)** | **1.75 GB** | 3,600 lossless trace files: prefill and generation for all 1,800 questions; 868,657 tokens, with selected expert IDs and effective weights at every layer. |
| **[Texts, metrics, derived data and viewer — ZIP](https://github.com/IvanPanzera/fnmr-qwen3.8-flash-next/releases/download/source-bundle-v1/fnmr-site-v1.zip)** | **33.9 MB** | Original questions and answers, English reading editions, token IDs and text, timings, experiment configuration, domain matrices, filter curves, hotlist rankings/profiles, provenance hashes and the viewer source. |

Sizes are decimal. These are the published `source-bundle-v1` release assets. Extract both ZIPs into the same folder to obtain the complete `docs/` and `data/traces/` layout. You can also [browse the immutable dataset](https://github.com/IvanPanzera/fnmr-qwen3.8-flash-next/tree/dataset-v1) or clone this repository.

### Choose the format you need

- **One table for a token, question mean or domain mean:** select it in [Router Lab](https://ivanpanzera.github.io/fnmr-qwen3.8-flash-next/) and click **Export matrix CSV**. The CSV contains all 24,576 layer/expert weights (48 × 512), including zeros and values hidden by the display filter. It opens in Excel and other spreadsheet tools.
- **All original token traces:** use `data/traces/<question-id>/prefill.fnr.gz` and `generation.fnr.gz`. These are the same compact, lossless FNR1 packets loaded by the viewer. Each token stores 48 × 10 selected expert IDs (`uint16`) and weights (`float32`); the remaining experts have zero effective weight. The [format specification](https://ivanpanzera.github.io/fnmr-qwen3.8-flash-next/methodology.html) and [JavaScript decoder](docs/data.js) describe how to reconstruct the full 48 × 512 table for every token.
- **Text, token labels and measurements:** `docs/data/questions/<question-id>.json` contains the original and English text, `input_ids` / `input_tokens`, `output_ids` / `output_token_text`, `token_seconds`, phase durations, throughput and trace checksums. Token positions follow array order; the interface numbers them from one. Layer and expert IDs start at zero.
- **Precomputed results:** `docs/data/matrices/` holds domain means, `docs/data/curves/` holds exact filter curves, and `docs/data/hotlists/` holds rankings and profiles. Compressed JSON files can be opened with any gzip reader. Question means are computed from the complete token traces; the [reference calculations](docs/math.js) are included.

The compact files preserve the recorded numeric values while avoiding a separate, mostly zero-filled table for every token. SHA-256 hashes for individual traces are included in the question JSON files and provenance metadata.

<details>
<summary>Archive SHA-256 checksums</summary>

```text
fnmr-traces-v1.zip  148230868030b609b3de05a0ca7a8d63ade910eecaf47a5a939e5a94147d7547
fnmr-site-v1.zip    01fd9f6971059ccda835a78c43768138bee5304e18f7c9eb50a609fae800143a
```

</details>

### The collection

| Property | Value |
|---|---|
| Questions | 1,800; 150 in each of 12 domains |
| Domains | Code generation, debugging, data analysis, mathematics, logic, engineering, science, documents, extraction, translation, professional writing, creative writing |
| Traced tokens | 518,884 prefill + 349,773 generation = 868,657 |
| Router | 48 layers, 512 routed experts per layer, 10 selected experts per token/layer |
| Split | 1,435 training questions; 365 held-out questions from separate task families |
| Collection completed | 8 October 2026, 22:18:44 UTC |
| Aggregate throughput with tracing | Prefill 133.72 tokens/s; generation 30.11 tokens/s |
| Original output cap | 384 tokens; reached by 97 answers |

The collection uses synthetic Italian task instructions. It was balanced down from a planned 3,600 questions to 1,800. Each domain has 20 task families; zero-based families 4, 9, 14 and 19 are held out. The split evaluates hotlist routing coverage, not answer correctness.

### What the colors mean

Each cell is the **effective normalized router weight after top-10 selection**, for one layer and one expert. The other 502 experts have zero effective weight. These are measured routing decisions, not neuron activations, unselected router logits, an intelligence score, or evidence that a named expert has a unique semantic function. “Functional neural MoE routing” is the project's name and visualization analogy; this is an independent project.

For a question mean, every token in the selected phase has equal weight. Domain means can weight each question equally or each token equally. Filtering hides weights strictly below the threshold without renormalization. Automatic filters choose a threshold subject to a maximum excluded router mass in every layer of each question mean or each original token, as selected. Ties remain visible. Witnesses identify the largest excluded mass.

### Recorded execution profile

The original experiment used the Nebula 2.1 diagnostic engine with the locally identified **Qwen3.8-Flash-Next GSQ-RCO IQ3_S (ISTA-DASLab)** target weights, a separate compatible draft model, context 2,048, prefill chunk 2,048, speculative window 4, minimum draft probability 0.5, INT8 KV cache, 13 workers, PCIe fraction 0.34, and 1,504 GPU-resident layer–expert pairs. Remaining experts ran on the CPU; residency did not remove experts from the model. The sampled free-VRAM minimum was 1,028 MiB across 9,445 samples, against a 1,024 MiB reserve.

The target's recorded first shard is 54,817,524,224 bytes, SHA-256 `4c1eb2ceb4915e1192f4f386021897bde56a97f40a0bb78bb86465e0f7d2aca3`. Model weights are external to this repository. Model and runtime labels describe the recorded local artifacts.

Instrumentation overhead is included in the displayed timings. Rejected speculative draft inputs are excluded from the accepted trace. Where necessary, a final diagnostic forward pass captured the last emitted token; that pass is excluded from generation timing and recorded separately. Aggregate rates are total tokens divided by summed phase duration, not an average of individual rates. This historical collection does not provide a controlled old-versus-new Nebula comparison.

### Hotlists and limits

There are 48 train-only profiles: 12 domains × prefill/generation × equal-question/equal-token averaging. Each ranks 1,504 layer–expert pairs globally, with no fixed per-layer quota. The UI shows held-out router mass covered by each profile and by the original global profile. These derived profiles were not applied during collection. Coverage does not measure answer accuracy or the speed achieved by applying a profile.

Answers may contain mistakes, incomplete code or truncated reasoning. No answer-quality scores are supplied. The English questions translate the task templates while preserving literal payloads. Answers combine Google Translate and direct editorial translations prepared on 16 October 2026; already-English answers are retained. Code, formulas and numerical literals are protected. A separate English glossary explains comments and labels in preserved code and structured data. The translations are reading aids and may introduce errors. Original text and SHA-256 hashes remain available. Translated text was never fed to the measured model.

### Files and reproducibility

- `docs/`: static browser application and compact metadata, question/answer text, exact domain means and filter curves.
- `data/traces/`: all 3,600 losslessly packed prefill/generation traces, approximately 1.75 GB compressed.
- `docs/data/provenance.json`: source and exported trace hashes, plus round-trip verification for all 1,800 questions.
- `docs/data/summary.json`: collection totals and per-domain results.
- `docs/data/hotlists/`: rankings and downloadable profiles.
- `tools/reference/`: original corpus, data model, hotlist and filter-analysis routines.
- `tools/export_assets.py`: export and byte-for-byte trace verification from the original campaign layout.
- `tests/`: numerical comparison against the original Python filter analysis, and collection integrity checks.

Clone the repository (about 1.8 GB), run `python -m http.server 8769`, and open `http://127.0.0.1:8769/docs/`. Run `npm test` with Node.js 20 or newer. The viewer uses browser gzip decompression and loads only the selected question's traces. The hosted page reads traces from the immutable `dataset-v1` tag; domain-level filtering uses exact precomputed curves.

See [methodology and trace format](https://ivanpanzera.github.io/fnmr-qwen3.8-flash-next/methodology.html). For reuse, retain the collection date, configuration, original-versus-translated distinction, and timing limitations. Please cite the repository and the exact commit or dataset tag.

Translation methods: Google Translate, direct editorial translation, and retention of already-English text. English editions are reading aids; the method, source hash and translated text hash are recorded per question.
