from ETS2LA.plugins.plugin import PluginInformation
PluginInfo = PluginInformation(
    name="Test",
    description="Test plugin",
    version="0.1",
    author="Test"
)

def plugin(runner):
    data = runner.GetData(["Test"])
    return "test"