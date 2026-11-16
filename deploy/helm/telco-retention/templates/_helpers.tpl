{{/* Labels shared by every object, plus the component name. */}}
{{- define "telco.labels" -}}
app.kubernetes.io/part-of: {{ .root.Chart.Name }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/* Selector labels: must never change after the first install. */}}
{{- define "telco.selector" -}}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}
