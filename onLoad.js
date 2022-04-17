if (typeof lua === 'undefined') {
  const getScript = (script_src) => {
    return new Promise((resolve, reject) => {
      const sc = document.createElement('script');
      [sc.async, sc.src, sc.type] = [true, script_src, 'text/javascript']
      sc.onerror = reject
      sc.onload = sc.onreadystatechange = () => {
        if (this.readyState && !/loaded|complete/.test(this.readyState)) return
        resolve()
      }
      document.head.appendChild(sc)
    })
  }

  const libURL = 'https://cdn.jsdelivr.net/gh/MegophrysNasuta/Mudlexus'
  const libVer = get_variable('MUDLEXUS_VERSION') || '0.1.3'

  getScript(`${libURL}@${libVer}/mudletShim.lua.bundle.js`).then(() => {
    console.log(`Loaded Nasuta's Mudlet Lua shim v${libVer}`)
    lua.execute('print("Lua is working!")')
  }).catch((e) => {
    console.error(`Could not load Mudlet Lua shim: ${e}`)
  })
}
