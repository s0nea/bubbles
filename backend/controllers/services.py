# bubbles - a simplified management UI for Ceph
# Copyright (C) 2021 SUSE, LLC
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
from enum import Enum
from mgr_module import MgrModule
from typing import Dict, List
from pydantic import BaseModel
from bubbles.backend.errors import BubblesError


class ServiceError(BubblesError):
    pass


class ServiceNotFoundError(ServiceError):
    pass


class ServiceStatusEnum(int, Enum):
    OKAY = 0
    WARN = 5
    ERROR = 10
    NONE = 20


class ServiceStatusCodeEnum(str, Enum):
    UNDEFINED = "undefined"
    DNE = "dne"


class ServiceStatusInfo(BaseModel):
    code: ServiceStatusCodeEnum
    msg: str


class ServiceStatusModel(BaseModel):
    name: str
    status: ServiceStatusEnum
    info: List[ServiceStatusInfo]


class ServiceTypeEnum(str, Enum):
    FILE = "file"
    OBJECT = "object"
    BLOCK = "block"


class ServiceBackendEnum(str, Enum):
    CEPHFS = "cephfs"
    NFS = "nfs"
    RBD = "rbd"
    ISCSI = "iscsi"
    RGW = "rgw"


class ServiceInfoModel(BaseModel):
    name: str
    size: int
    replicas: int
    type: ServiceTypeEnum
    backend: ServiceBackendEnum

    @property
    def raw_size(self) -> int:
        return self.replicas * self.size


class ServiceModel(BaseModel):
    info: ServiceInfoModel
    pools: List[int]

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def size(self) -> int:
        return self.info.size

    @property
    def raw_size(self) -> int:
        return self.info.raw_size

    @property
    def type(self) -> ServiceTypeEnum:
        return self.info.type

    @property
    def backend(self) -> ServiceBackendEnum:
        return self.info.backend


class ServiceStateModel(BaseModel):
    services: Dict[str, ServiceModel]


class ServicesController:

    _mgr: MgrModule
    _services: Dict[str, ServiceModel] = {}

    def __init__(self, mgr: MgrModule):
        self._mgr = mgr
        self._load()

    @property
    def services(self) -> List[ServiceInfoModel]:
        return [svc.info for svc in self._services.values()]

    def get(self, name: str) -> ServiceInfoModel:
        if name not in self._services:
            raise ServiceNotFoundError()
        return self._services[name].info

    @property
    def total_allocated(self) -> int:
        allocated = sum([svc.raw_size for svc in self._services.values()])
        return allocated

    async def create(self, info: ServiceInfoModel) -> bool:
        if not self.is_valid(info):
            return False

        if info.name in self._services:
            return False

        self._services[info.name] = ServiceModel(info=info, pools=[])
        self._save()
        return True

    async def status(self, svcname: str) -> ServiceStatusModel:
        status = ServiceStatusModel(
            name=svcname, status=ServiceStatusEnum.NONE, info=[]
        )
        if svcname not in self._services:
            status.status = ServiceStatusEnum.ERROR
            status.info.append(
                ServiceStatusInfo(
                    code=ServiceStatusCodeEnum.DNE, msg="does not exist"
                )
            )
            return status
        return status

    def is_valid(self, info: ServiceInfoModel) -> bool:
        return (
            len(info.name) > 0
            and len(info.type) > 0
            and len(info.backend) > 0
            and info.size > 0
            and info.replicas > 0
            and self._is_valid_type(info.type, info.backend)
        )

    def _is_valid_type(
        self, type: ServiceTypeEnum, backend: ServiceBackendEnum
    ) -> bool:

        if type == ServiceTypeEnum.FILE:
            return (
                backend == ServiceBackendEnum.CEPHFS
                or backend == ServiceBackendEnum.NFS
            )
        elif type == ServiceTypeEnum.OBJECT:
            return backend == ServiceBackendEnum.RGW
        else:
            assert type == ServiceTypeEnum.BLOCK
            return (
                backend == ServiceBackendEnum.RBD
                or backend == ServiceBackendEnum.ISCSI
            )

    def _save(self) -> None:
        state = ServiceStateModel(services=self._services)
        svcstr = state.json()
        self._mgr.set_store("services", svcstr)

    def _load(self) -> None:
        svcstr = self._mgr.get_store("services")
        if not svcstr or len(svcstr) == 0:
            return
        state = ServiceStateModel.parse_raw(svcstr)
        self._services = state.services
