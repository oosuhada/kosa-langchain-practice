import asyncio

# 비동기(코루틴) 함수 정의
async def work1():
    print("비동기 작업1 시작")
    # 대기 및 제어권을 이벤트 루프로 반환 -> 이 작업은 멈춰있지만 쓰레드 자체가 멈추는 것은 아니며 다른 비동기 작업 실행.
    await asyncio.sleep(2)
    # 2초 후에 다시 제어권을 가져와서 다음 작업 실행
    print("비동기 작업1 완료")
    return "작업1 결과"

# 비동기(코루틴) 함수 정의
async def work2():
    print("비동기 작업2 시작")
    # 대기 및 제어권을 이벤트 루프로 반환 -> 이 작업은 멈춰있지만 쓰레드 자체가 멈추는 것은 아니며 다른 비동기 작업 실행.
    await asyncio.sleep(1)
    # 1초 후에 다시 제어권을 가져와서 다음 작업 실행
    print("비동기 작업2 완료")
    return "작업2 결과"

# 메인 비동기 함수 정의
async def main(): # 메인 진입점
    # 비동기 작업을 이벤트 루프에 등록
    task1 = asyncio.create_task(work1()) # 작업1 등록
    task2 = asyncio.create_task(work2()) # 작업2 등록
    # 대기 및 제어권을 이벤트 루프로 반환 -> 다른 비동기 작업 실행
    await asyncio.sleep(0) # 쓰레드가 멈추지 않고 다른 작업 실행
    # 비동기 작업 완료 대기
    await task1 # 작업1 완료 대기
    await task2 # 작업2 완료 대기
    # task1과 task2이 끝날때까지 기다린 후 결과 출력
    print("모든 작업 완료")
    
# 어플리케이션 시작: main() 실행
asyncio.run(main())
    