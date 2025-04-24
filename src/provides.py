# Copyright 2025 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from charms import reactive
from cosl import DashboardPath40UID, LZMABase64

from charmhelpers.core import hookenv

from .lib.cos_agent import CosAgentProviderUnitData


@dataclass
class MetricsEndpoint:
    port: int
    path: str = "/metrics"
    # cos-agent is an interface with a subordinate charm, therefore
    # localhost should be a sane default
    host: str = "localhost"
    job_name: str = "default"
    dashboards_dir: Optional[str] = None
    _job_prefix: str = ""

    @property
    def job_prefix(self):
        return self._job_prefix

    @job_prefix.setter
    def job_prefix(self, value):
        self._job_prefix = value

    def to_dict(self):
        return {
            "job_name": f"{self.job_prefix}{self.job_name}",
            "metrics_path": self.path,
            "static_configs": [{"targets": [f"{self.host}:{self.port}"]}],
        }


class CosAgentProvides(reactive.Endpoint):

    MetricsEndpoint = MetricsEndpoint

    @reactive.when("endpoint.{endpoint_name}.joined")
    def joined(self):
        hookenv.log(
            "{}: {} -> {}".format(
                self._endpoint_name,
                type(self).__name__,
                inspect.currentframe().f_code.co_name,
            ),
            level=hookenv.INFO,
        )
        reactive.set_flag(self.expand_name("{endpoint_name}.connected"))

    @reactive.when("endpoint.{endpoint_name}.changed")
    def changed(self):
        hookenv.log("COS Agent interface changed", level=hookenv.DEBUG)
        reactive.set_flag(self.expand_name("{endpoint_name}.available"))

    @reactive.when("endpoint.{endpoint_name}.departed")
    def departed(self):
        reactive.clear_flag(self.expand_name("{endpoint_name}.connected"))
        reactive.clear_flag(self.expand_name("{endpoint_name}.available"))

    def update_cos_agent(
        self, metrics_endpoints: Optional[List[MetricsEndpoint]] = None
    ):
        metrics_endpoints = metrics_endpoints or []
        scrape_config = []
        dashboards = []
        for index, endpoint in enumerate(metrics_endpoints):
            endpoint.job_prefix = self.expand_name("{endpoint_name}_") + f"{index}_"
            scrape_config.append(endpoint.to_dict())
            dashboards.extend(self._encode_dashboards(endpoint.dashboards_dir))
        hookenv.log(f"Updating scrape config: {scrape_config}", level=hookenv.DEBUG)

        data = CosAgentProviderUnitData(
            metrics_alert_rules={},
            log_alert_rules={},
            dashboards=dashboards,
            metrics_scrape_jobs=scrape_config,
            log_slots=[],
            tracing_protocols=[],
        )

        for rel in self.relations:
            rel.to_publish[data.KEY] = data.model_dump()

    @staticmethod
    def _encode_dashboards(dashboard_dir: Optional[str]) -> List[str]:
        """Prepare Grafana dashboards so that they may be shared via relation.

        :param dashboard_dir: Path to a directory that holds exported (.json)
                               grafana dashboard files.
        """
        if dashboard_dir is None:
            return []

        dashboards: List[str] = []
        charm_name = hookenv.charm_name()
        for path in Path(dashboard_dir).glob("*.json"):
            hookenv.log(f"Processing dashboard: {path}", level=hookenv.DEBUG)
            with open(path, "rt") as dashboard_file:
                dashboard = json.load(dashboard_file)
            rel_path = str(
                path.relative_to(hookenv.charm_dir()) if path.is_absolute() else path
            )
            # COSAgentProvider is somewhat analogous to GrafanaDashboardProvider.
            # We need to overwrite the uid here because there is currently no other
            # way to communicate the dashboard path separately.
            # https://github.com/canonical/grafana-k8s-operator/pull/363
            dashboard["uid"] = DashboardPath40UID.generate(charm_name, rel_path)

            # Add tags
            tags: List[str] = dashboard.get("tags", [])
            if not any(tag.startswith("charm: ") for tag in tags):
                tags.append(f"charm: {charm_name}")
            dashboard["tags"] = tags

            dashboards.append(LZMABase64.compress(json.dumps(dashboard)))
        return dashboards
