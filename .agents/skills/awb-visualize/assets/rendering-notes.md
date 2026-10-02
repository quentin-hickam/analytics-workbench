# Rendering notes

Checked 2026-10-02. Refresh these notes when a host changes behavior, then revise the output contract in the [skill](../SKILL.md) only to the confidence re-established here. "User-confirmed" means the analyst observed it in their own setup; it is not documented behavior.

## Confirmed

| Claim | Basis |
| --- | --- |
| VS Code Copilot Chat displays a generated Python plot PNG from the workspace inline. | User-confirmed. VS Code documents that media "from tool results" and "inlined in assistant messages" open in the chat image carousel (`imageCarousel.chat.enabled`, on by default since 1.113): <https://code.visualstudio.com/docs/chat/chat-overview>, <https://code.visualstudio.com/updates/v1_113> |
| VS Code chat renders Mermaid: through the `renderMermaidDiagram` tool since 1.109, and in Markdown chat output through the built-in Mermaid extension since 1.121. | <https://code.visualstudio.com/updates/v1_109>, <https://code.visualstudio.com/updates/v1_121> |
| VS Code chat renders arbitrary HTML only through an extension's chat output renderer (webview), not from HTML in a response. | <https://code.visualstudio.com/updates/v1_103> |
| Visual Studio 2022 17.14 and later render Mermaid returned in Copilot Chat. | <https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes> |
| Word, Outlook, Excel, and PowerPoint for Microsoft 365 insert SVG. | <https://support.microsoft.com/en-us/office/graphics-visuals/edit-svg-images-in-microsoft-365> |
| Google Docs and Sheets accept PNG, JPG, and GIF under 50 MB; SVG is not supported. | <https://support.google.com/docs/answer/9224754> |
| Microsoft 365 compresses inserted pictures to 220 ppi by default unless high fidelity or no compression is chosen. | <https://support.microsoft.com/en-us/office/graphics-visuals/reduce-the-file-size-of-a-picture-in-microsoft-office>, <https://support.microsoft.com/en-us/office/graphics-visuals/change-the-default-resolution-for-inserting-pictures-in-office> |
| Matplotlib PNGs carry a 200 dpi `pHYs` value and arbitrary `metadata` text keys. | Tested locally with matplotlib 3.10.0 and seaborn 0.13.2. |
| seaborn `errorbar=` replaced `ci=` in 0.12; 0.13 needs `hue` to apply a palette and accepts polars frames; `seaborn.objects` is documented as experimental. | <https://seaborn.pydata.org/tutorial/error_bars.html>, <https://seaborn.pydata.org/whatsnew/v0.13.0.html>, <https://seaborn.pydata.org/tutorial/objects_interface.html> |

## Uncertain

- Whether VS Code chat renders a Markdown image that points to a workspace-relative path, a remote URL, or a data URI. A community report says remote URLs do not render (<https://github.com/orgs/community/discussions/192581>); no official statement was found for the other two.
- What Copilot Chat on github.com renders inline. GitHub documents Mermaid generation in Copilot Chat for use in issues, pull requests, and discussions (<https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook/communicate-effectively/creating-diagrams>), not inline rendering of Mermaid or images in the chat pane.
- Whether Word sizes a pasted PNG from its `pHYs` dpi or from pixel dimensions. Check the inserted width and set it to 6.5 in when needed.
- What a copy from rendered chat Markdown pastes into Word, Outlook, or Google Docs. Raw Markdown pasted into desktop Word stays literal pipe text according to secondary sources; no Microsoft statement was found.
- Mermaid in Word, Outlook, or Google Docs: no documented support; treat Mermaid source as text there.
- Chat panel pixel width varies with the user's layout; the image carousel gives full-size zoom.
