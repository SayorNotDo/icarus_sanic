from BaseModel import BaseModel
from tortoise.queryset import (
    QuerySet,
    QuerySetSingle,
)
from typing import (
    TypeVar,
    Optional,
    TYPE_CHECKING,
)

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model

MODEL = TypeVar("MODEL", bound="Model")


class BaseRepository:
    MODEL_CLASS = BaseModel
    SAVE_BATCH_SIZE = 1000

    def save(self, obj) -> bool:
        if not obj:
            return False
        obj.save()
        return True

    def save_batch(self, objs, *, batch_size=SAVE_BATCH_SIZE) -> bool:
        if not objs:
            return False
        self.MODEL_CLASS.objects.bulk_save(objs, batch_size=batch_size)
        return True

    def delete(self, obj) -> bool:
        if not obj:
            return False
        obj.delete()
        return True

    def delete_batch(self, objs) -> bool:
        if not objs:
            return False
        for obj in objs:
            self.delete(obj)
        return True

    def delete_batch_by_query(self, filter_kw: dict, exclude_kw: dict) -> bool:
        self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw).delete()
        return True

    def delete_by_fake(self, obj) -> bool:
        if obj is None:
            return False
        obj.is_deleted = True
        obj.save()
        return True

    def update(self, obj) -> bool:
        if not obj:
            return False
        obj.save()
        return True

    def update_batch(self, objs) -> bool:
        if not objs:
            return False
        for obj in objs:
            self.update(obj)
        return True

    def update_batch_by_query(self, filter_kw: dict, exclude_kw: dict,
                              newattrs_kwargs: dict) -> bool:
        self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw).update(**newattrs_kwargs)

    def query(self, filter_kw: dict,
              exclude_kw: dict) -> QuerySetSingle[Optional[MODEL]]:
        return self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw).first()

    def query_set(self, filter_kw: dict, exclude_kw: dict,
                  order_bys: list) -> QuerySet[MODEL]:
        query_result = self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw)
        if order_bys:
            query_result.order_by(*order_bys)
            return query_result

    def query_all(self, filter_kw: dict, exclude_kw: dict,
                  order_bys: list) -> list:
        return self.query_set(filter_kw, exclude_kw, order_bys)

    def exists(self, filter_kw: dict, exclude_kw: dict) -> bool:
        return self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw).exists()

    def count(self, filter_kw: dict, exclude_kw: dict) -> int:
        return self.MODEL_CLASS.objects.filter(**filter_kw).exclude(
            **exclude_kw).count()
