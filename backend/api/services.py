# bubbles - a simplified management UI for Ceph
# Copyright (C) 2021 SUSE, LLC
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
from typing import Dict, List
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from bubbles.bubbles import Bubbles
from bubbles.backend.controllers.services import (
    ServiceInfoModel,
    ServiceStatusModel,
)


class ListReply(BaseModel):
    allocated: int = Field(0, title="Allocated bytes, total")
    services: List[ServiceInfoModel] = Field([], title="Services")
    status: Dict[str, ServiceStatusModel] = Field(
        {}, title="status per service"
    )


router = APIRouter(prefix="/services", tags=["services"])


@router.get("/list", response_model=ListReply)
async def get_list(request: Request) -> ListReply:
    bubbles: Bubbles = request.app.state.bubbles
    assert bubbles.ctrls.services is not None

    allocated = bubbles.ctrls.services.total_allocated
    svcs = bubbles.ctrls.services.services

    status: Dict[str, ServiceStatusModel] = {}
    for svc in svcs:
        status[svc.name] = await bubbles.ctrls.services.status(svc.name)

    return ListReply(allocated=allocated, services=svcs, status=status)


@router.post("/create", response_model=bool)
async def create(request: Request, info: ServiceInfoModel) -> bool:
    bubbles: Bubbles = request.app.state.bubbles
    assert bubbles.ctrls.services is not None
    return await bubbles.ctrls.services.create(info)
