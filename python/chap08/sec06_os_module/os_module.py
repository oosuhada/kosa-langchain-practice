# 시스템 정보 얻기 - os 사용
import os

if __name__ == "__main__":
    # 현재 파일 및 현재 폴더의 절대 경로 얻기
    print(
        __file__
    )  # __file__은 현재 모듈의 파일 경로를 나타내는 특수 변수. 실행 방식에 따라 상대 경로로 나올 수도 있음

    print(os.path.abspath(__file__))  # 현재 모듈 파일의 절대 경로를 출력

    print(
        os.path.abspath(".")
    )  # 현재 작업 디렉토리(.)의 절대 경로를 출력. 현재 모듈이 있는 폴더와 항상 같은 것은 아님

    print(
        os.getcwd()
    )  # 현재 작업 디렉토리의 절대 경로를 출력, cwd는 current working directory의 약자

    print("-" * 50)

    # 현재 폴더 안에 있는 파일의 목록 얻기
    print(os.listdir(os.getcwd()))  # 현재 작업 디렉토리 안의 파일/폴더 목록 출력

    files = os.listdir(".")  # "."은 현재 작업 디렉토리를 의미함

    for file in files:
        abs_path = os.path.abspath(file)
        abs_path2 = os.path.join(os.getcwd(), file)

        print("-" * 50)
        print(abs_path)
        print(abs_path2)

        if os.path.isfile(abs_path):
            print(file)  # 현재 작업 디렉토리에 있는 파일 이름을 출력

        if os.path.isdir(abs_path):
            print("[DIR]", file)  # 현재 작업 디렉토리에 있는 폴더 이름을 출력
        else:
            print(file)  # 폴더가 아닌 경우 파일 또는 기타 항목 이름을 출력

    print("-" * 50)

    # 폴더 생성
    target_dir = os.path.join(os.getcwd(), "dir1", "dir12")

    # os.mkdir(target_dir)
    # os.mkdir()은 마지막 폴더 하나만 생성한다.
    # 중간 폴더(dir1)가 없으면 에러가 발생할 수 있다.

    os.makedirs(
        target_dir, exist_ok=True
    )  # exist_ok=True는 이미 폴더가 존재하는 경우에도 에러를 발생시키지 않고 넘어가도록 하는 옵션

    # 폴더 삭제
    if os.path.exists(
        target_dir
    ):  # exists()는 파일이나 폴더가 존재하는지 여부를 확인하는 함수
        os.rmdir(target_dir)  # dir12 폴더 삭제. 비어 있는 폴더만 삭제 가능
        os.rmdir(
            os.path.dirname(target_dir)
        )  # dir1 폴더 삭제. 비어 있는 폴더만 삭제 가능

    # 명령어 실행
    os.system("ls")  # Mac/Linux에서는 "ls" 명령어로 현재 폴더 목록을 출력한다.
    # os.system("dir")  # Windows에서는 "dir" 명령어로 현재 폴더 목록을 출력한다.
    # 참고로 print(os.system("ls"))처럼 쓰면 파일 목록 출력 후 마지막에 0도 출력된다.
    # os.system()은 명령어 실행 결과 코드도 반환하기 때문이다. 정상 실행이면 보통 0이 출력된다.
    # 목록만 보고 싶으면 os.system("ls")처럼 print 없이 사용하면 된다.

    print("-" * 50)

    print(os.name)
    # Mac/Linux에서는 보통 "posix"가 출력된다.
    # Windows에서는 보통 "nt"가 출력된다.

    print(os.uname())
    # Mac/Linux 기준: os.uname()으로 운영체제 정보를 확인할 수 있다.
    # Windows 기준: os.uname()은 지원되지 않을 수 있다.
    # Windows까지 고려하면 hasattr(os, "uname")으로 확인 후 사용하는 것이 안전하다.

    print(os.system("ls"))
    # Mac/Linux 기준: "ls" 명령어로 현재 폴더 목록을 출력한다.
    # Windows 기준: "ls" 대신 "dir" 명령어를 사용한다.
    # os.system()은 명령어 실행 결과 코드도 반환한다. 정상 실행이면 보통 0이 출력된다.
