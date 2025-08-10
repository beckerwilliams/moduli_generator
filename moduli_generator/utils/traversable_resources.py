from importlib.resources.abc import TraversableResources


class ModuliTraversableResources(TraversableResources):

    def __init__(self, package):
        super().__init__()
        self.package = package

    def open_resource(self, path):
        super().open_resource()

    def is_resource(self, path):
        super().is_resource()

    def contents(self):
        super().contents()

    def path(self, path):
        super().path()


TraversableResources.register(ModuliTraversableResources)


for resource in resources.contents("data.bash_scripts"):

    data_path = resources.path("data.bash_scripts", resource)
    print(f"data_path: {data_path}")


resources = ModuliTraversableResources("data.bash_scripts")

# Loaders that wish to support resource reading should implement a get_resource_reader(fullname)
# method as specified by importlib.resources.abc.ResourceReader.
