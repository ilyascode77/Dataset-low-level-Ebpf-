# Storage Layout

This directory defines the hostPath PV/PVC layer for VM1.

## PV/PVC Mapping

| Host path | PV | PVC | Namespace | Purpose |
|---|---|---|---|---|
| `/srv/pfe-lab/ecommerce` | `pv-ecommerce-benign` | `pvc-ecommerce` | `benign-lab` | e-commerce data |
| `/srv/pfe-lab/ecommerce` | `pv-ecommerce-attack` | `pvc-ecommerce-attack` | `attack-lab` | controlled attack access to e-commerce test data |
| `/srv/pfe-lab/fio` | `pv-fio` | `pvc-fio` | `benign-lab` | fio workload |
| `/srv/pfe-lab/filebench` | `pv-filebench` | `pvc-filebench` | `benign-lab` | filebench workload |
| `/srv/pfe-lab/shared` | `pv-shared-benign` | `pvc-shared-benign` | `benign-lab` | benign shared data |
| `/srv/pfe-lab/shared` | `pv-shared-attack` | `pvc-shared-attack` | `attack-lab` | attack shared data |

## Why Multiple PVs For The Same HostPath

A Kubernetes PV binds to one PVC. For a single-node research lab, we use multiple explicit PVs pointing to the same safe hostPath directory to model shared data across namespaces.
