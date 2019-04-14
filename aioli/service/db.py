# -*- coding: utf-8 -*-

import orm

from aioli.core.manager import DatabaseManager
from aioli.exceptions import DatabaseError, NoMatchFound
from .base import BaseService


class DatabaseService(BaseService):
    """Service class providing an interface with common database operations

    :ivar __model__: Peewee.Model
    :ivar db_manager: Aioli database manager (peewee-async)
    """

    __model__: orm.Model
    db_manager: DatabaseManager

    @classmethod
    def register(cls, pkg, mgr):
        super(DatabaseService, cls).register(pkg, mgr)
        cls.db_manager = mgr.db

    @property
    def model(self):
        if not self.__model__:
            raise Exception(f'{self.__class__.__name__}.__model__ not set, unable to perform database operation')

        return self.__model__

    def _model_has_attrs(self, *attrs):
        for attr in attrs:
            if not hasattr(self.model, attr):
                raise Exception(f'Unknown field {attr}', 400)

        return True

    def _parse_sortstr(self, value: str):
        if not value:
            return []

        model = self.model

        for col_name in value.split(','):
            sort_asc = True
            if col_name.startswith('-'):
                col_name = col_name[1:]
                sort_asc = False

            if self._model_has_attrs(col_name):
                sort_obj = getattr(model, col_name)
                yield sort_obj.asc() if sort_asc else sort_obj.desc()

    def _get_query_filtered(self, query, **control):
        query = self.__model__.objects.filter(**query).limit(limit).offset(offset)

        if sort:
            order = self._parse_sortstr(sort)
            return query.order_by(*order)

        return query

    async def get_many(self, **query):
        #query = self._get_query_filtered(expression, **kwargs)
        #return [o for o in await self.db_manager.execute(query)]

        sort = query.pop('_sort', None)
        limit = query.pop('_limit', 0)
        offset = query.pop('_offset', 0)

        return [o.__dict__ for o in await self.model.objects.filter(**query).all()]

    async def get_one(self, **query):
        try:
            rv = await self.model.objects.get(**query)
            return rv.__dict__
        except (orm.exceptions.MultipleMatches, KeyError) as e:
            self.log.exception(e)
            raise DatabaseError
        except orm.exceptions.NoMatch:
            raise NoMatchFound

    async def create(self, item: dict):
        return await self.db_manager.create(self.model, **item)

    async def get_or_create(self, item: dict):
        return await self.db_manager.get_or_create(self.model, **item)

    async def count(self, expression=None, **kwargs):
        query = self._get_query_filtered(expression, **kwargs)
        return await self.db_manager.count(query)

    async def update(self, record, payload):
        if not isinstance(record, peewee.Model):
            record = await self.get_one(record)

        for k, v in payload.items():
            setattr(record, k, v)

        await self.db_manager.update(record)
        return record

    async def delete(self, record_id: int):
        record = await self.get_one(record_id)
        deleted = await self.db_manager.delete(record)
        return {'deleted': deleted}
