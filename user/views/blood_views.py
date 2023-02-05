from datetime import datetime, timedelta

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from user.models import Info, BloodSugarLevel
from user.serializers import BloodDietSerializer, BloodSerializer


# 식후 혈당량 api
class BloodSugarLevelView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 같은 그룹 내의 식후 혈당량 가져오기
        try:
            blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False).order_by(
                '-created_at__date', 'timeline')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BloodDietSerializer(blood_list, many=True, context={"request": request})

        # 날짜별로 데이터 묶기
        res_data = []
        prev_date = ''  # 현재 탐색 날짜
        data = []  # 식후 혈당량 리스트
        for blood in serializer.data:
            if blood["date"] == prev_date:
                data.append(blood)
            else:
                if prev_date is not '':
                    res_data.append({"date": prev_date[3:8], "data": data})
                data = [blood]
                prev_date = blood["date"]
        res_data.append({"date": prev_date[3:8], "data": data})  # 마지막 날짜 데이터
        return Response(res_data, status=status.HTTP_200_OK)

    def post(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 당뇨인이 아니라면 등록 거부
        if user.is_diabetes is False:
            return Response({"error": "당뇨인 본인만 혈당을 입력할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # request body 데이터 유효성 검사
        serializer = BloodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 그룹 내 오늘의 식단 정보 맞는지 검사
        try:
            diet_data = BloodSugarLevel.objects.get(id=request.data["id"], user_id__group=user.group_id)
        except:
            return Response({"error": "존재하지 않는 식단입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 식후 혈당량 이미 있는지 검사
        if diet_data.level is not None:
            return Response({"error": "식후 혈당량 값이 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(validated_data=request.data)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        try:
            diet_data = BloodSugarLevel.objects.get(id=request.data["id"], user_id__group=user.group_id)
            diet_data.level = 0
            diet_data.time = ""
            diet_data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 주간 혈당 리포트 api
class BloodLevelReportView(APIView):
    def get_blood_level(self, blood_sugar_level):
        if blood_sugar_level >= 140:  # 고혈당
            return 3
        elif blood_sugar_level >= 70:  # 정상 혈당
            return 2
        else:  # 저혈당
            return 1

    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 해당 그룹의 당뇨인 정보 가져오기
        user_diabetes = Info.objects.filter(group_id=user.group_id, is_diabetes=True)

        if user_diabetes.count() == 0:  # 아직 그룹에 당뇨인이 없다면
            return Response({"error": "아직 그룹에 당뇨인이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 현재 날짜 가져오기
        end_date = datetime.now().date()  # 현재 날짜
        start_date = end_date - timedelta(days=6)  # 일주일 전 날짜
        join_date = user_diabetes[0].created_at.date()  # 가입 날짜

        # 아직 가입 후 일주일이 안지났다면
        empty_date_cnt = 0
        if start_date < join_date:
            empty_date_cnt = (join_date - start_date).days
            start_date = join_date

        # 요일 별 혈당량 평균과 저혈당, 정상혈당, 고혈당 개수 세기
        data = []
        cur_date = start_date
        blood_level = [0, 0, 0, 0]  # 1: 저혈당 요일 수, 2: 정상 혈당 요일 수, 3: 고혈당 요일 수
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        while cur_date <= end_date:
            date_level_avg = BloodSugarLevel.objects.filter(created_at__date=cur_date).values('created_at__date'). \
                annotate(Avg('level')).filter(user_id__group=user.group_id, level__isnull=False)
            if date_level_avg.count() == 0:
                data.append({"day": days[cur_date.weekday()], "level": 0})
            else:
                day = date_level_avg[0]["created_at__date"].weekday()
                level = self.get_blood_level(date_level_avg[0]["level__avg"])
                blood_level[level] += 1
                data.append({"day": days[day], "level": level})
            cur_date += timedelta(days=1)  # 하루 더하기

        # 일주일 안 지났을 경우 빈 칸 채워주기
        for i in range(1, empty_date_cnt + 1):
            empty_date = end_date + timedelta(days=i)
            day = empty_date.weekday()
            data.append({"day": days[day], "level": 0})

        res_data = {
            "name": user_diabetes[0].name,
            "start": start_date.strftime('%Y.%m.%d')[2:10],
            "end": end_date.strftime('%Y.%m.%d')[5:10],
            "low": blood_level[1],
            "common": blood_level[2],
            "high": blood_level[3],
            "data": data
        }
        return Response(res_data, status=status.HTTP_200_OK)
