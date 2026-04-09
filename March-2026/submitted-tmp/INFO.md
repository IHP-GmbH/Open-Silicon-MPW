## Submission processing

The designs were processed internally using two scripts: `conv2sub.py` and `zerp.py`.

- `conv2sub.py` ensures that the correct options are set when saving the final GDS.
- `zerp.py` removes zero-area polygons.

To detect zero-area polygons in KLayout, move the `zero_poly.lydrc` macro to
`$PDK_ROOT/$PDK/libs.tech/klayout/tech/macros`, then restart KLayout.

After restarting, an additional menu item becomes available. Once executed, the
zero-area polygons appear in the Marker Browser.
