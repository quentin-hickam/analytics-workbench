# Process, lineage, and relationship diagrams

Use Mermaid for chat where the host supports it. The dated [rendering notes](../assets/rendering-notes.md) distinguish VS Code tool rendering from Markdown rendering and document other host evidence; consult them when host support is uncertain. Keep source in a fenced `mermaid` block when rendering is unconfirmed, including github.com chat. For chat delivery, accompany the Mermaid diagram with a compact structure table so its relationships remain available as text.

Documents do not render Mermaid. For a document-bound diagram, export PNG with mermaid-cli when installed, or when the user approves installing it:

```bash
mmdc -i diagram.mmd -o diagram.png -w 1300 -b white
```

Check the actual export dimensions; the viewport option alone may not produce the required image width. Follow [figure delivery](figure-delivery.md) for the exported image, including opacity, dimensions, accessibility, and evidence metadata. If export is unavailable, a textual list or structure table is the complete fallback deliverable; report that the image was not exported.

Before delivery, verify every node and relationship against the source, labels are legible, and the diagram and structure table agree. Numerical claims also obey the shared analytical contract.
