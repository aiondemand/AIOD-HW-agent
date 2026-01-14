from hw_agent.repositories.base_repository import BaseRepository


class RepositoryFactory:
    _registry = {}

    @classmethod
    def register(cls, key):
        def decorator(repository_cls):
            cls._registry[key] = repository_cls
            return repository_cls
        return decorator

    @classmethod
    def create_repository(cls, repository_type) -> BaseRepository:
        repository_cls = cls._registry.get(repository_type)
        if repository_cls is None:
            raise ValueError(f"Unsupported repository type: {repository_type}. Please, check the environment variable REPOSITORY_TYPE")
        return repository_cls()
