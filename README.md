# mec_wheel
전자과 캡디 코드(위성재급유 시스템)

launch 파일에 10초 뒤 시작한다는 설정을 넣었습니다.

작동 시나리오
1. 탐색
처음에는 Aruco Marker 안보임
Depth camera를 이용하여 위성 벽면과의 거리를 1.5m로 유지하며, 위성 주변을 오른쪽으로(매그넘 휠 기준) 즉 위에서 보면 반시계 방향으로 둥글게 돔.(게걸음 원궤도 비행)

- angular.y = abs(MAV_V) / 1.5 로 설정해둠.
원운동 공식 v = r * w로 인해 r = 1.5, v = 0.3m/s 이므로 w값이 저렇게 설정 됨.

2. 조준 및 정렬
카메라에 Aruco Marker가 발견 시, Depth camera말고 RGB camera 사용.
매그넘휠은 Marker가 카메라 화면 한가운데 올 때까지 속도를 줄이면서 정렬을 시작함.
Marker와 각도가 틀어져있으면 매그넘휠의 heading을 돌려 시선을 맞추고, 좌우 오차가 5cm 이내가 될 때까지 정렬함.

- 중심에서 5cm 이내로 들어왔는가?(좌우 오차 5cm 이내)
-> abs(marker_x) < 0.05
로 구현.

- 카메라의 FOV는 가로87도 x 세로58도임.
코드에 FOV의 반인 43.5를 self.HALF_FOV_RAD로 설정.

(1) theta = math.atan2(abs(marker_x), marker_z)
카메라 정면 기준 마커가 좌우로 얼마나 치우쳐져 있는지 각도를 arctan 삼각함수로 구함.

(2) w = min(theta / HALF_FOV_RAD, 1.0)
구한 각도를 0부터 1 사이의 퍼센트로 정규화 시킴.
화면 맨 끝에 마커가 있으면 1(100%), 화면 정중앙에 있으면 0(0%)이 됨.

(3) msg.linear.y = MAX_V * w
퍼센트를 속도에 곱해줌. 마커가 멀리 있으면 속도가 높고, 마커가 카메라의 중앙에 가까워질수록 속도가 0으로 수렴을 하게 됨.

(4) msg.linear.x = 1.0 * (marker_z - 1.5)
1.5m를 유지해야하므로 이 코드를 넣음. 현재 거리가 1.6m로 멀어지면 0.1의 속도로 전진, 1.4m로 가까워지면 -0.1의 속도로 후진

(5) msg.angular.y = -0.5 * marker_x
마커가 화면 중심(x=0)에 오도록 고개를 돌려주는 역할

3. 전진
완벽하게 일직선으로 정렬이 되면, 매그넘휠은 1.5m 거리에서 30cm 앞까지 천천히 직진함.

4. 도킹 완료 및 신호 전달
30cm 거리에 도달 시 로봇은 모든 바퀴를 멈춤.
'Stopped'라는 신호를 publish함.

좌표계
매그넘휠의 중심(0,0,0) 기준임.
1. 전진/후진 : linear.z(z축)
2. 옆으로 가기 : linear.x(x축, 양수면 오른쪽)
3. 제자리 회전 : angular.y(y축 수직 기준)

4. 마커의 좌/우 : marker_x(x축, +면 우측, -면 좌측)
5. 마커의 앞/뒤 : marker_z(앞쪽 거)

통신 데이터
subscribers
1. /aruco_poses(geometry_msgs/PoseArray)
Aruco Marker가 매그넘휠로부터 얼마나 떨어져있는지 알려주는 좌표(X, Z)
2. /target_depth(std_msgs/Float32)
Marker가 안 보일 때 위성 외벽까지의 거리를 알려주는 Depth 센서 값
(급발진 방지를 위해 0.1m ~ 3.0m 사이의 값만 받는다고 설정. 만약 이 범위가 아닐 경우 has_depth가 false가 되어 linear.x와 angular.y만 실행됨.)
publishers
1. /cmd_vel(geometry_msgs/Twist)
실제 주행 명령
2. /wheel_status(std_msgs/String)
현재 로봇의 상태를 알려줌. 이동 중일 때는 moving, 30cm 앞 정지가 되면 stopped를 publish함.
