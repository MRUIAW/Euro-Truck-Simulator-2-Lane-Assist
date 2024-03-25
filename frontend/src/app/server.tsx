// Communicate with the ETS2LA backend web server on 37520
async function GetVersion() {
    console.log("Getting version")
    const response = await fetch("http://localhost:37520/")
    const data = await response.json()
    console.log(data)
}

async function CloseBackend() {
    console.log("Closing backend")
    const response = await fetch("http://localhost:37520/api/quit")
    const data = await response.json()
    console.log(data)
}

async function GetFrametimes() {
    console.log("Getting frametimes")
    const response = await fetch("http://localhost:37520/api/frametimes")
    const data = await response.json()
    return data
}

async function GetPlugins(): Promise<string[]> {
    const response = await fetch("http://localhost:37520/api/plugins")
    const data = await response.json()
    return data
}

async function DisablePlugin(plugin: string) {
    console.log("Disabling plugin")
    const response = await fetch(`http://localhost:37520/api/plugins/${plugin}/disable`)
    const data = await response.json()
    console.log(data)
}

async function EnablePlugin(plugin: string) {
    console.log("Enabling plugin")
    const response = await fetch(`http://localhost:37520/api/plugins/${plugin}/enable`)
    const data = await response.json()
    console.log(data)
}

export { GetVersion, CloseBackend, GetFrametimes, GetPlugins, DisablePlugin, EnablePlugin }