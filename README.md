# Openstack Glance Exporter

This exporter expose metrics for monitoring Glance service in openstack.

## Metrics
Name | Type | Label |Description
---------|---------|---------|-------------
glance_api_availability | Gauge | status | Check availability of Glance API
glance_panel_images_sync | Gauge | state | Check if images on panel are synchronized with IaC
