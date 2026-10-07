# Nova

```
terminal.log("Hello Nova!")
```

> Hello Nova!

이 언어는 파이썬을 기반으로 만들어진 인터프리터 언어입니다.

# 구현 방법

다음 명령을 실행하여 Nova 언어를 설치합니다

```bash
pip install git+https://github.com/HshMaker/Nova

그 후에 다음 명령으로 nova 파일을 실행합니다.

nova file.nova
```

# 문법

## 입력 및 출력

기본 내장 팩 `terminal`에서 출력을 다룹니다.

```
terminal.log("HshMaker is the best.")
```

> HshMaker is the best.

```
terminal.warn("주의!")
```

> <span style=color:#E2E44F;>[warn] 주의!</span>

`terminal.err("error")`로 에러를 출력할 수도 있고 `terminal.clear()`로 터미널을 청소할 수도 있습니다.

```
terminal.write("입력: ") << 사용자의 입력을 받습니다.
```

## 변수

변수를 선언하기 위해선 var 예약어를 사용합니다.

```
var nova: string = "nova" << nova라는 변수에 문자열 "nova"를 넣습니다.
```

콜론 뒤 자료형은 생략가능합니다. (자동 캐스팅 지원)

추가로 Nova는 총 6가지 자료형이 있습니다.
`string, int, float, bool, object, array`

이 중에서 배열 변수를 선언할 때는 무조건 배열 안의 자료형을 지정해줘야합니다.

```
잘못된 예시
var list: array = [] << 오류가 발생합니다.
var list: array<int> = ["hi"] << 오류가 발생합니다.

좋은 예시
var list: array<int> = []
var list: array<int> = [1, 3]
```

만약 초기 값을 지정하고 싶지 않다면 any를 사용할 수 있습니다.

```
var list: array<any> = []

list.push(1) << 이때 list의 자료형이 array<int>로 정해집니다.
```

## if문

다음과 같이 if문을 사용합니다.

```
var nova: int = 3

if (nova < 4) then
    terminal.log(nova)
end
```

> 3

if문 블럭은 반드시 end로 끝나야합니다.

또 other를 이용해서 그 밖에 다른 경우를 구현할 수 있습니다.

```
var nova: int = 11

if (nova < 4) then
    terminal.log(nova)
other if (nova < 10) then
    terminal.log("조금 큰 수")
other then
    terminal.log("많이 큰 수")
end
```

> 많이 큰 수

## 반복문

Nova는 반복문으로 `repeat` 문법을 사용합니다.

```
var i: int = 0
repeat (i < 5) then
    terminal.log(i)
    i  = i + 1
end
```

> 0 1 2 3 4 (줄바꿈은 생략)

## 함수

Nova는 함수 선언을 위해 `fun`을 사용합니다.

```
fun add(a: int, b: int): int then
    return a + b
end
```

이처럼 반환 자료형을 지정해줄 수도 있고 각 매개변수의 자료형 지정을 생략할 수도 있습니다.

또 여러개의 매개변수를 list로 받을 수도 있습니다.

```
fun ellipsis(a: int, ...remains: int ) then
    terminal.log(remains)
end

ellipsis(1, 2, 3, 4)
```

> [2, 3, 4]

## 팩

Nova는 class 대신 pack을 사용합니다.

```
pack Test then
    #init(a: int) then
        #a = a
    end

    #appear() then
        return #a
    end
end
```

위와 같이 선언합니다. 내장 함수로는 팩이 선언될 때 실해되는 `init` 함수
불러올 때 실행되는 `appear` 함수가 있습니다.

팩을 선언한 뒤에는 자료형에 선언한 팩이 추가됩니다. 즉, 다음과 같이 사용가능합니다.

```
var nova: Test = Test(0)
```

## send, take at

다른 파일에 있는 팩(pack)이나 함수에 접근할 때는 `send`와 `take at`을 사용합니다.

```
// 위에 있는 Test 팩을 send합니다.
send Test
```

그 후 `take at`으로 가져옵니다.

```
take Test at "[경로]"

var nova: Test = Test(0)
```

경로는 상대경로를 이용합니다.

# 예시

다음 주소에서 예시 코드들을 확인하실 수 있습니다.
[github/Hshmaker/Nova/nova/testcodes](https://github.com/HshMaker/Nova/tree/main/nova/testcodes)

### 개발 철학

중괄호는 disgusting하다.

예약어들은 누가봐도 알아 볼 수 있게 해야한다.

많은 기호는 디버깅을 해친다.

줄구분은 명확하게 하자.

### TODOS

- [x] add terminal and utils class
- [x] add variables
- [x] add data type checking system
- [x] add if other
- [x] add repeat loop
- [x] add function and its functions
- [x] code highlighting / auto completing
- [x] add logical operators
- [x] add array
- [x] add take at send (import from export)
- [x] add array type auto casting
- [x] add object
- [x] support pack send
- [x] add random (nova file)
- [ ] add pack (class) 50% complete
- [ ] add file reading
- [ ] Array self hosting
