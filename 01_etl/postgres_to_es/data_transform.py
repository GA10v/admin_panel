import json

from components import models
from components.settings import Settings


class DataTransformer:
    # Сделал для выполнения условия (- валидируйте конфигурации с помощью `pydantic`)
    def prepare_data(self, pg_data: list[models.PGDataConf]) -> list[models.ESDocument]:
        """Подготовка данных из PostgreSQL к отправки в Elasticserch.

        Args:
            pg_data: Список словарей с данными из PostgreSQL.

        Returns:
            prepared_data: Список объектов модели ESDocument.
        """
        self.pg_data = [item for item in pg_data][0]
        prepared_data = []
        dates = []
        for item in self.pg_data:
            entry = models.ESDocument(
                id=item.get('id'),
                imdb_rating=item.get('imdb_rating'),
                genre=item.get('genres'),
                title=item.get('title'),
                description=item.get('description'),
                director=item.get('director'),
                actors_names=item.get('actors_names'),
                writers_names=item.get('writers_names'),
                actors=item.get('actors'),
                writers=item.get('writers'),
            )
            update_time = item.get('modified')
            prepared_data.append(entry)
            dates.append(update_time)
        self.last_update_time = max(dates)
        return prepared_data

    def compile_data(self, pg_data: list[models.PGDataConf]) -> list[models.ESDataConf]:
        """
        Подготовка bulk для загрузки в Elasticserch.

        Args:
            pg_data: Список словарей с данными из PostgreSQL.

        Returns:
            bulk: Список словарей для загрузки в Elasticserch.
        """
        entries = self.prepare_data(pg_data)
        bulk = []
        for entry in entries:
            index = {
                'index': {
                    '_index': Settings().es_index,
                    '_id': str(entry.id),
                },
            }
            document = {
                'id': str(entry.id),
                'imdb_rating': entry.imdb_rating,
                'genre': entry.genre,
                'title': entry.title,
                'description': entry.description,
                'director': entry.director,
                'actors_names': entry.actors_names,
                'writers_names': entry.writers_names,
                'actors': entry.actors,
                'writers': entry.writers,
            }
            bulk.append(json.dumps(index))
            bulk.append(json.dumps(document))
        bulk = '\n'.join(bulk) + '\n'
        return bulk

    def get_last_update_time(self) -> str:
        """
        Определение даты последнео изменения данных.

        Returns:
            last_update_time: Дата последнего изменения данных.
        """
        return self.last_update_time
