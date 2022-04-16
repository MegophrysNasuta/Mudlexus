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

const libURL = 'https://cdn.jsdelivr.net/gh/MegophrysNasuta/Mudlexus@1.0'

getScript(`${libURL}/mudletShim.lua.bundle.js`).then(() => {
  console.log("Loaded Nasuta's Mudlet Lua shim")
  console.log(lua.execute('print("Lua is working!")'))
}).catch((e) => {
  console.error(`Could not load Mudlet Lua shim: ${e}`)
})
