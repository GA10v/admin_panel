from components import models, utilities, constants
from pg_extractor import PostgresExtractor
import datetime
import json


class DataTransform:
    # Сделал для выполнения условия (- валидируйте конфигурации с помощью `pydantic`)
    def prepare_data(self, pg_data: list[models.PGDataConf]) -> list[models.ESDocument]:
        """
        Подготовка данных из PostgreSQL к отправки в Elasticserch

        Args:
            pg_data: Список словарей с данными из PostgreSQL

        Returns:
            es_data: Список объектов модели ESDocument
        """

        self.pg_data = [x for x in pg_data][0]
        es_data = []
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
            es_data.append(entry)
        return es_data

    def compile_data(self, pg_data: list[models.PGDataConf]) -> list[dict]:
        """
        Подготовка bulk для загрузки в Elasticserch

        Args:
            pg_data: Список словарей с данными из PostgreSQL

        Returns:
            bulk: Список словарей для загрузки в Elasticserch
        """

        entries = self.prepare_data(pg_data)
        bulk = []
        for entry in entries:
            index = {
                'index': {
                    '_index': constants.ES_INDEX,
                    '_id': str(entry.id)
                }
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
            bulk.append(index)
            bulk.append(document)
        return bulk


if __name__ == '__main__':
    with utilities.pg_conn_context(constants.DSL_PG) as pg_conn:
        pg_loader = PostgresExtractor(connection=pg_conn, batch_size=1000)
        pg_data = pg_loader.get_data(last_update_time=datetime.datetime.now())

        es_data = DataTransform().compile_data(pg_data)

        print(len(es_data))

        with open('2.json', 'w') as f:
            json.dump(es_data, f, indent=4, ensure_ascii=False)
