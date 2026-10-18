<div align="center">

  <a href="https://github.com/NousResearch/hermes-agent">
    <img src="https://github.com/user-attachments/assets/ac2f5702-c842-4b2e-9340-737481fa0ece" width="96" height="96" alt="Nous Research Hermes mark" />
  </a>

  # Pantheon

  **Ten gods for your Hermes desktop.**

  Ten themes for Hermes Desktop, each with its own myth and its own palette, drawn in dithered marble.
  Install once and switch with a word.

  <sub>FOR <a href="https://github.com/NousResearch/hermes-agent">HERMES DESKTOP</a> &nbsp;·&nbsp; COMMUNITY THEMES &nbsp;·&nbsp; VERSION 0.2.0</sub>

  <br /><br />

  [See all ten live](https://adolanium.github.io/hermes-pantheon/) &nbsp;·&nbsp; [Try it in a minute](#try-it-in-a-minute) &nbsp;·&nbsp; [Meet the ten](#meet-the-ten) &nbsp;·&nbsp; [Switch any time](#switch-any-time)

</div>

![Ten narrow columns side by side, one per theme, each with a dithered marble head at the top, the theme's name inscribed vertically in the middle, and a collage of statue fragments at the bottom, every column in its own palette from indigo to parchment](media/banner.png)

## Try it in a minute

You need Hermes Desktop 0.22.2 or later. You don't need a terminal.

**1. Install.** In Hermes Desktop, open **Capabilities → Plugins** and click **Install from Git**. Paste this address, click **Review repository**, then install:

```text
https://github.com/Adolanium/hermes-pantheon
```

<details>
<summary>Prefer the terminal?</summary>

<br />

```sh
hermes plugins install Adolanium/hermes-pantheon
```

If it asks whether to enable the plugin, either answer works. That switch is for the agent side, and Pantheon has nothing there.

</details>

**2. Turn it on.** **Pantheon** now appears in **Capabilities → Plugins**. Flip its **Desktop** switch on. Desktop plugins installed from a package start turned off, and this is the step people miss.

**3. Pick a god.** Type this in the message box and press Enter:

```text
/skin olympus
```

The whole app changes on the spot, with no restart. Try `/skin hades` next, or plain `/skin` to step through every theme you have.

## Meet the ten

Click a card to see the full window.

| [![Olympus: indigo and lavender, Zeus reaching for a star](media/cards/olympus.png?v=0.2.0)](media/shots/olympus.png?v=0.2.0) | [![Nyx: pure black and white, the night goddess under her starfield](media/cards/nyx.png?v=0.2.0)](media/shots/nyx.png?v=0.2.0) |
|:---:|:---:|
| [![Hades: charcoal and ember, the underworld throne](media/cards/hades.png?v=0.2.0)](media/shots/hades.png?v=0.2.0) | [![Poseidon: abyssal teal and seafoam, the trident raised](media/cards/poseidon.png?v=0.2.0)](media/shots/poseidon.png?v=0.2.0) |
| [![Helios: bronze and gold, the sun chariot](media/cards/helios.png?v=0.2.0)](media/shots/helios.png?v=0.2.0) | [![Selene: slate and silver, the moon rising](media/cards/selene.png?v=0.2.0)](media/shots/selene.png?v=0.2.0) |
| [![Athena: olive and sage, spear and owl](media/cards/athena.png?v=0.2.0)](media/shots/athena.png?v=0.2.0) | [![Aphrodite: wine and rose, rising from the shell](media/cards/aphrodite.png?v=0.2.0)](media/shots/aphrodite.png?v=0.2.0) |
| [![Medusa: black and acid green, Perseus and the gorgon](media/cards/medusa.png?v=0.2.0)](media/shots/medusa.png?v=0.2.0) | [![Caduceus: parchment and ink, Hermes in flight](media/cards/caduceus.png?v=0.2.0)](media/shots/caduceus.png?v=0.2.0) |

## Switch any time

Every Pantheon theme is a normal Hermes theme, so all the usual ways to switch work:

| Where | What to do |
| --- | --- |
| **Message box** | `/skin <name>`, for example `/skin selene`. `/skin list` shows every theme; `/skin` alone moves to the next one. |
| **Command palette** | Press <kbd>Ctrl</kbd> <kbd>K</kbd> (<kbd>⌘</kbd> <kbd>K</kbd> on macOS), choose **Change theme**, and pick one. |
| **Settings** | **Settings → Appearance → Theme**. |

The names are `olympus`, `nyx`, `hades`, `poseidon`, `helios`, `selene`, `athena`, `aphrodite`, `medusa` and `caduceus`. To go back to the stock look, type `/skin nous`.

Hermes remembers your choice for each profile, so a work profile can live on Olympus while a personal one lives on Hades.

## Small decisions, already made

- **One install, ten themes.** All ten ship in a single plugin. There's nothing to choose at install time and nothing extra to download later.
- **The art lives inside the plugin.** Every statue is a dithered image packed into `plugin.js`, and the fonts (IBM Plex) are bundled too, so themes switch instantly and work fully offline.
- **Your light or dark setting can't break the art.** Each theme keeps its own palette in both modes. Caduceus is the light one; the other nine are dark.
- **The accent picker still works.** Pick a custom accent in Settings and the theme keeps its art and framing.
- **The chat stays readable.** The art sits in the sidebar and the empty new-session screen. Once a conversation starts, it's text on a calm ground.

## Update or remove

```sh
hermes plugins update hermes-pantheon
hermes plugins remove hermes-pantheon
```

Or use **Capabilities → Plugins**: switch **Pantheon** off to hide the themes, or remove it from there. If a Pantheon theme was active, Hermes goes back to its default theme.

## What it touches

- **Theme registration** through the Desktop plugin SDK, the same way any theme plugin adds itself to the picker.
- **Style rules** that apply only while a Pantheon theme is active, and disappear when you switch away.
- **IBM Plex Sans and IBM Plex Mono** for the interface, plus one display face per god for the HERMES AGENT wordmark, all bundled inside the plugin under the [SIL Open Font License](LICENSES).

It makes no network requests, adds no agent tools, hooks, background processes or settings, and reads none of your data.

The bracketed tabs, dotted rules and placement of the art style Hermes Desktop's own markup, because the plugin SDK has no slots for decoration yet. If a Desktop update renames that markup, those touches fall back to the plain palette. Nothing else breaks.

## Compatibility

| Hermes Desktop | Platform | Status |
| --- | --- | --- |
| 0.22.2 | Windows 11 | Tested |
| 0.22.2 | macOS, Linux | Expected to work; not yet tested |

<br />

<div align="center">
  <strong>Pantheon</strong><br />
  <sub>Ten gods, one command.</sub>
</div>

<br />

## License

[MIT](LICENSE). The bundled fonts are under the SIL Open Font License: IBM Plex, and the gods' wordmark faces (Silkscreen, Grenze Gotisch, Cinzel Decorative, Cinzel, Marcellus SC, Forum, Gloock, Metamorphous, IM Fell English SC), plus Bodoni Moda on the site. See [LICENSES](LICENSES).

> **Community project**
>
> Pantheon is an independent community theme pack. It is not affiliated with, endorsed by, sponsored by, or officially associated with [Nous Research](https://github.com/NousResearch) or the [Hermes Agent project](https://github.com/NousResearch/hermes-agent). Hermes, Hermes Agent, and Nous Research are names and marks belonging to their respective owners.
