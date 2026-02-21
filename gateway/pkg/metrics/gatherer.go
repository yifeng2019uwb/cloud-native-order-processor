package metrics

import (
	"strings"

	"github.com/prometheus/client_golang/prometheus"
	dto "github.com/prometheus/client_model/go"
)

const createdSuffix = "_created"

// filterCreatedGatherer wraps a prometheus.Gatherer and removes any metric family
// whose name ends with "_created" (Unix timestamp, often shown as ~1.77G in Grafana).
type filterCreatedGatherer struct {
	g prometheus.Gatherer
}

// Gather implements prometheus.Gatherer.
func (f *filterCreatedGatherer) Gather() ([]*dto.MetricFamily, error) {
	got, err := f.g.Gather()
	if err != nil {
		return nil, err
	}
	out := make([]*dto.MetricFamily, 0, len(got))
	for _, mf := range got {
		if mf.Name != nil && strings.HasSuffix(*mf.Name, createdSuffix) {
			continue
		}
		out = append(out, mf)
	}
	return out, nil
}

// Handler returns an http.Handler that exposes Prometheus metrics from the default
// gatherer, excluding *_created metrics to avoid timestamp series (e.g. 1.77G) in Grafana.
func Handler() prometheus.Gatherer {
	return &filterCreatedGatherer{g: prometheus.DefaultGatherer}
}
