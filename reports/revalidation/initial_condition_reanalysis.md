# Initial-condition reanalysis

The original 20-point grid was rerun without changing chemistry, constants, pools, or grid values.
Every case used current-tolerance BDF and Radau; all four 0.004 M iodate cases also used
BDF and Radau with rtol/atol tightened by 10x.

| Quantity | Original report | Resolved-limit-cycle reanalysis |
|---|---:|---:|
| qualifying cases | 15 | 12 |
| period range (s) | 449.958059 to 1726.81135 | 449.958233 to 561.775382 |
| iodine peak range (M) | 2.12229816e-09 to 0.000336893228 | 4.359818e-05 to 0.000336893228 |

The digitized single-cycle period 714.13 s is **outside** the revised resolved envelope.
The former `PARTIALLY` period conclusion is therefore not retained.

## Nonlinear interaction

The original maximum period interaction was 669.479135 s. It depended on 0.004 M
iodate trajectories that do not satisfy the numerical-resolution criterion. Restricting the
diagnostic to resolved trajectories gives 0.00210074215 s; the ~669 s interaction does not survive.
