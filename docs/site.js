// The colonnade: one column per theme, one open. Opening a column (click, arrow keys,
// the /skin box, a name chip, or #name in the URL) swings it wide, reveals the
// real screenshot through an ordered dither, and moves the page to its palette.
;(() => {
  const THEMES = window.PANTHEON
  const byName = Object.fromEntries(THEMES.map(t => [t.name, t]))
  const root = document.documentElement
  const colonnade = document.getElementById('colonnade')
  const reduced = matchMedia('(prefers-reduced-motion: reduce)')
  const narrow = matchMedia('(max-width: 860px)')
  let current = null

  const el = (tag, props = {}, children = []) => {
    const node = Object.assign(document.createElement(tag), props)
    for (const child of children) node.append(child)
    return node
  }

  // ── Build the columns ───────────────────────────────────────────────────
  document.documentElement.style.setProperty('--n', THEMES.length)

  const cols = THEMES.map(t => {
    const col = el('article', { className: 'col' })
    col.dataset.name = t.name
    for (const [k, v] of Object.entries({ bg: t.bg, ink: t.ink, dim: t.dim, rule: t.rule, send: t.send, 'send-ink': t.sendInk })) {
      col.style.setProperty(`--c-${k}`, v)
    }

    const tab = el('button', { className: 'col-tab', type: 'button' }, [
      el('span', { className: 'col-head' }),
      el('span', { className: 'col-name', textContent: t.label }),
      el('span', { className: 'col-foot' })
    ])
    tab.querySelector('.col-head').style.backgroundImage = `url(assets/art/${t.name}-top.png)`
    tab.querySelector('.col-foot').style.backgroundImage = `url(assets/art/${t.name}-bottom.png)`
    tab.setAttribute('aria-expanded', 'false')
    tab.setAttribute('aria-controls', `body-${t.name}`)
    tab.setAttribute('aria-label', `${t.label}: ${t.description}`)
    tab.addEventListener('click', () => open(t.name))
    tab.addEventListener('pointerenter', () => preload(t.name))
    tab.addEventListener('focus', () => preload(t.name))

    const img = el('img', { alt: `Hermes Desktop wearing the ${t.label} theme: ${t.description}.`, decoding: 'async' })
    img.width = 1440
    img.height = 900
    const canvas = el('canvas')
    canvas.setAttribute('aria-hidden', 'true')

    const chip = el('button', { className: 'skin-chip', type: 'button' }, [
      el('span', { textContent: `/skin ${t.name}` }),
      el('span', { textContent: 'Copy' })
    ])
    chip.setAttribute('aria-label', `Copy /skin ${t.name}`)
    chip.addEventListener('click', () => copy(`/skin ${t.name}`, chip.lastChild, 'Copy'))

    const swatches = el('ul', { className: 'swatches' }, [t.bg, t.tone, t.rule, t.ink].map(c => {
      const li = el('li')
      li.style.background = c
      li.title = c.toUpperCase()
      return li
    }))
    swatches.setAttribute('aria-label', 'Palette')

    const body = el('div', { className: 'col-body', id: `body-${t.name}` }, [
      el('figure', { className: 'window' }, [
        el('div', { className: 'window-bar' }, [
          el('span', { className: 'dots' }, [el('i'), el('i'), el('i')]),
          el('span', { className: 'title', textContent: `${t.name}.theme` }),
          el('span', { className: 'hint', textContent: 'Hermes Desktop' })
        ]),
        el('div', { className: 'shot' }, [img, canvas])
      ]),
      el('div', { className: 'caption' }, [
        el('div', {}, [
          el('h2', { textContent: t.label }),
          el('p', { textContent: t.description + '.' }),
          el('p', { className: 'myth', textContent: t.myth })
        ]),
        el('div', { className: 'caption-side' }, [swatches, chip])
      ])
    ])
    body.setAttribute('role', 'region')
    body.setAttribute('aria-label', `${t.label} theme`)

    col.append(tab, body)
    colonnade.append(col)
    return col
  })

  const colFor = name => cols.find(c => c.dataset.name === name)

  // ── Images ──────────────────────────────────────────────────────────────
  const srcFor = name => (narrow.matches || innerWidth < 1100 ? `assets/shots/${name}-720.webp` : `assets/shots/${name}.webp`)
  const preload = name => {
    const img = colFor(name).querySelector('.shot img')
    if (!img.getAttribute('src')) img.src = srcFor(name)
    return img.decode ? img.decode().catch(() => {}) : Promise.resolve()
  }

  // ── The dither reveal: the screenshot appears through an 8x8 Bayer screen ─
  const BAYER = [0, 32, 8, 40, 2, 34, 10, 42, 48, 16, 56, 24, 50, 18, 58, 26, 12, 44, 4, 36, 14, 46, 6, 38, 60, 28, 52, 20, 62, 30, 54, 22,
    3, 35, 11, 43, 1, 33, 9, 41, 51, 19, 59, 27, 49, 17, 57, 25, 15, 47, 7, 39, 13, 45, 5, 37, 63, 31, 55, 23, 61, 29, 53, 21]

  const reveal = (canvas, color) => {
    const box = canvas.getBoundingClientRect()
    if (reduced.matches || !box.width) {
      canvas.width = canvas.height = 0
      return
    }
    const dpr = Math.min(devicePixelRatio || 1, 2)
    const cell = Math.round(4 * dpr)
    canvas.width = Math.round(box.width * dpr)
    canvas.height = Math.round(box.height * dpr)
    const g = canvas.getContext('2d')
    g.fillStyle = color
    g.fillRect(0, 0, canvas.width, canvas.height)
    const cols = Math.ceil(canvas.width / cell)
    const rows = Math.ceil(canvas.height / cell)
    const duration = 620
    let cleared = 0
    const start = performance.now()
    const frame = now => {
      const t = Math.min(1, (now - start) / duration)
      const target = Math.floor((1 - (1 - t) ** 3) * 64)
      for (; cleared < target; cleared++) {
        const i = BAYER.indexOf(cleared)
        const ox = i % 8
        const oy = (i / 8) | 0
        for (let y = oy; y < rows; y += 8) for (let x = ox; x < cols; x += 8) g.clearRect(x * cell, y * cell, cell, cell)
      }
      if (t < 1) requestAnimationFrame(frame)
      else canvas.width = canvas.height = 0
    }
    requestAnimationFrame(frame)
  }

  // ── Opening a column ────────────────────────────────────────────────────
  const paint = t => {
    const vars = { bg: t.bg, ink: t.ink, dim: t.dim, rule: t.rule, tone: t.tone, surface: t.surface, send: t.send, 'send-ink': t.sendInk, muted: t.muted }
    for (const [k, v] of Object.entries(vars)) root.style.setProperty(`--${k}`, v)
    root.toggleAttribute('data-light', t.light)
    document.querySelector('meta[name="theme-color"]').content = t.bg
  }

  const open = (name, { scroll = false, push = true } = {}) => {
    const t = byName[name]
    if (!t || name === current) return
    current = name

    for (const col of cols) {
      const isOpen = col.dataset.name === name
      col.classList.toggle('is-open', isOpen)
      col.querySelector('.col-tab').setAttribute('aria-expanded', String(isOpen))
    }
    const col = colFor(name)

    paint(t)
    const canvas = col.querySelector('canvas')
    preload(name).then(() => {
      if (current === name) setTimeout(() => reveal(canvas, t.bg), narrow.matches ? 120 : 300)
    })

    // The open god's own art below the fold, swapped through the same dither.
    for (const [sel, slot] of [['.god-head', 'top'], ['.god-foot', 'bottom'], ['.close-art', 'hero']]) {
      const box = document.querySelector(sel)
      const art = box.querySelector('img')
      art.onload = () => current === name && reveal(box.querySelector('canvas'), t.bg)
      art.src = `assets/art/${name}-${slot}.png`
    }

    document.getElementById('step-skin').textContent = `/skin ${name}`
    document.getElementById('step-skin-copy').dataset.copy = `/skin ${name}`
    for (const b of document.querySelectorAll('#name-list button')) b.toggleAttribute('aria-current', b.dataset.name === name)

    if (push) history.replaceState(null, '', `#${name}`)
    if (scroll) colonnade.scrollIntoView({ behavior: reduced.matches ? 'auto' : 'smooth', block: 'start' })
  }

  // Arrow keys walk the colonnade like tabs.
  colonnade.addEventListener('keydown', e => {
    const keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }
    if (!(e.key in keys) || !e.target.closest('.col-tab')) return
    e.preventDefault()
    const i = THEMES.findIndex(t => t.name === current)
    const next = THEMES[(i + keys[e.key] + THEMES.length) % THEMES.length].name
    open(next)
    colFor(next).querySelector('.col-tab').focus({ preventScroll: true })
  })

  // ── The /skin box, which behaves like the real command ──────────────────
  const form = document.getElementById('skin-form')
  const input = document.getElementById('skin-input')
  const status = document.getElementById('skin-status')
  const datalist = document.getElementById('skin-names')
  for (const t of THEMES) datalist.append(el('option', { value: t.name }))

  const say = text => {
    status.textContent = text
    clearTimeout(say.timer)
    say.timer = setTimeout(() => (status.textContent = ''), 4200)
  }

  form.addEventListener('submit', e => {
    e.preventDefault()
    const arg = input.value.trim().toLowerCase().replace(/^\/?skin\s*/, '')
    input.value = ''
    if (!arg || arg === 'next') {
      const i = THEMES.findIndex(t => t.name === current)
      const next = THEMES[(i + 1) % THEMES.length]
      open(next.name, { scroll: true })
      return say(`Switched to ${next.label}.`)
    }
    if (arg === 'list' || arg === 'ls') return say(THEMES.map(t => t.name).join(' · '))
    if (arg === 'nous' || arg === 'default') return say('Nous is the stock theme. In the app, /skin nous takes you back.')
    const t = byName[arg] || THEMES.find(x => x.label.toLowerCase() === arg)
    if (!t) return say(`No god called "${arg}". Try /skin list.`)
    open(t.name, { scroll: true })
    say(`Switched to ${t.label}.`)
  })

  // ── Name chips under "Switch any time" ──────────────────────────────────
  const nameList = document.getElementById('name-list')
  THEMES.forEach((t, i) => {
    const b = el('button', { type: 'button', textContent: t.name })
    b.dataset.name = t.name
    b.addEventListener('click', () => open(t.name))
    nameList.append(b, document.createTextNode(i < THEMES.length - 2 ? ', ' : i === THEMES.length - 2 ? ' and ' : ''))
  })

  // ── Copy buttons ────────────────────────────────────────────────────────
  const copy = async (text, label, idle) => {
    try {
      await navigator.clipboard.writeText(text)
      label.textContent = 'Copied'
    } catch {
      label.textContent = 'Select & copy'
    }
    const btn = label.closest('button') || label
    btn.dataset.done = ''
    setTimeout(() => {
      label.textContent = idle
      delete btn.dataset.done
    }, 1600)
  }
  for (const b of document.querySelectorAll('.copy')) b.addEventListener('click', () => copy(b.dataset.copy, b, 'Copy'))

  // The switch in step 2 flips once the steps come into view.
  const install = document.getElementById('install')
  new IntersectionObserver((entries, io) => {
    if (entries.some(e => e.isIntersecting)) {
      install.classList.add('in-view')
      io.disconnect()
    }
  }, { threshold: 0.35 }).observe(install)

  // ── Start: the god in the URL, else Olympus ─────────────────────────────
  const fromHash = () => location.hash.slice(1).toLowerCase()
  open(byName[fromHash()] ? fromHash() : 'olympus', { push: false })
  addEventListener('hashchange', () => byName[fromHash()] && open(fromHash(), { push: false }))
})()
