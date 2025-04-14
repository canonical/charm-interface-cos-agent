# Overview

This interface handles relation with [grafana agent charm][grafana-agent],
and by extension, integration with [COS][cos].

> [!IMPORTANT]
> This is an interface layer for [reactive charms][reactive] which are, at this point,
> surprased by [operator charms][operator]. Unless you are explicitly working
> on reactive charms, you are likely looking for
> [operator cos-agent library][cos-agent].

Grafana Agent charm provides [cos agent library][cos-agent] that implements
both sides of this relation. However, the library is compatible only with Operator
charms. This interface layer implements "provides" side of the same interface and
allows reactive charms to relate with Grafana Agent.

## Integration Dependencies

If you wish to use this interface layer in your charm, you need to explicitly
include its dependencies. Include contents of this repository's
[requirements.txt](./requirements.txt), to your charm's `wheelhouse.txt`

<!-- LINKS -->

[grafana-agent]: https://charmhub.io/grafana-agent
[cos]: https://charmhub.io/topics/canonical-observability-stack
[cos-agent]: https://charmhub.io/grafana-agent/libraries/cos_agent
[reactive]: https://charmsreactive.readthedocs.io/en/latest/
[operator]: https://ops.readthedocs.io/en/latest/
