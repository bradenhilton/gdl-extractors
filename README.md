<!-- markdownlint-disable MD033 -->

# gdl-extractors

Custom extractor modules for [gallery-dl](https://github.com/mikf/gallery-dl).

## Usage

Download extractor module `.py` files from [`extractor/`](extractor) to a directory of your choosing such as `~/.config/gallery-dl/modules`, then provide this directory as a [module source](https://gdl-org.github.io/docs/configuration.html#extractor-module-sources) in your gallery-dl config, e.g.:

<details open><summary><code>config.json</code></summary>

```json
{
    "extractor": {
        "module-sources": [
            "~/.config/gallery-dl/modules",
            null
        ]
    }
}
```

</details>
