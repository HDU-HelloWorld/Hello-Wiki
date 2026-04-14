from domain.ports.compile_port import CompilePort


class ScaffoldCompileService(CompilePort):
    def enqueue_compile(self, source_uri: str) -> str:
        raise NotImplementedError("Compile adapter is intentionally not implemented in MVP scaffold.")
