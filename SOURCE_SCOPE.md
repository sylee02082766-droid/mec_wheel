# Source and contribution scope

The executable source is based on the user's existing GitHub repository `sylee02082766-droid/mec_wheel`, revision `ef3b5d5` (2026-05-05). The original ROS2.zip archive was also inspected, but it contains different control constants, stop timing and a different full-platform launch. Those differences are **not** copied over the current published controller.

Changes in this cleanup: README, ignore rules, license text, dependency documentation and removal of student email from package metadata. Runtime source, console entry points and package resource hierarchy are preserved.

Other archived components remain outside this snapshot:

- `mirobot_transform_test`: teammate repository and student account metadata.
- `aruco_tf`, `mecanum_i2c_bridge`: team packages with root/TODO attribution/license metadata.
- `ros2_aruco`, `Wlkata_Mirobot_Ros2`: third-party libraries, drivers and meshes.
- Caches, build outputs, repository internals, binaries and unreviewed personal reports.

The root README describes the current public source and identifies the omitted components as dependencies of the full team experiment.
