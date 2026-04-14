from domain.ports.compile_port import CompilePort


class CompileApplicationService:
    def __init__(self, compile_port: CompilePort) -> None:
        self._compile_port = compile_port

    def compile_document(self, source_uri: str) -> str:
        try:
            return self._compile_port.enqueue_compile(source_uri)
        except NotImplementedError:
            return "MVP scaffold only, compile workflow is not implemented."
