# Azure Function Sample

iPad, GitHub, Codex, GitHub Actions, Azure Functions의 전체 개발 흐름을 확인하기 위한 Python 3.12 샘플입니다.

## 현재 기능

- `GET /api/health`: Function 상태 확인
- `POST /api/results`: JSON 요청을 검증하고 Azure Storage Queue에 저장
- 모든 JSON 응답과 Queue 메시지를 UTF-8로 처리
- Application Insights에서 추적할 수 있도록 `requestId` 기록
- 요청 본문 크기를 기본 48 KiB로 제한
- HTTP 엔드포인트에 Function Key 인증 적용

## 요청 예시

```json
{
  "source": "intune",
  "deviceName": "SAMPLE-PC-01",
  "result": "Succeeded",
  "message": "샘플 결과입니다."
}
```

정상적으로 접수되면 HTTP `202 Accepted`와 `requestId`를 반환하고, `intune-results` Queue에 다음 형식으로 저장합니다.

```json
{
  "schemaVersion": "1.0",
  "requestId": "...",
  "receivedAtUtc": "2026-08-24T00:00:00Z",
  "source": "intune",
  "payload": {}
}
```

## 로컬 설정

`local.settings.sample.json`을 복사하여 `local.settings.json`으로 만들고 개발 환경에 맞게 값을 설정합니다. 실제 `local.settings.json`은 Git에서 제외됩니다.

필수 애플리케이션 설정:

| 이름 | 용도 |
|---|---|
| `AzureWebJobsStorage` | Functions 호스트와 Queue 연결 |
| `RESULT_QUEUE_NAME` | 결과를 저장할 Queue 이름 |
| `MAX_REQUEST_BYTES` | 허용할 최대 요청 크기 |

## 보안 원칙

- 연결 문자열, Function Key, 인증서, 암호를 저장소에 커밋하지 않습니다.
- 운영 비밀정보는 Azure App Settings 또는 Key Vault에서 관리합니다.
- `local.settings.json`은 `.gitignore`와 `.funcignore`에서 제외합니다.
- 실제 장치 정보나 고객 로그를 테스트 데이터로 커밋하지 않습니다.
- GitHub Actions의 Azure 인증은 Publish Profile이 아닌 OIDC를 사용합니다.

## 다음 단계

1. Azure에 Python 3.12 Function App과 Storage Account 생성
2. `RESULT_QUEUE_NAME=intune-results` 설정
3. GitHub Actions OIDC 배포 연결
4. iPad에서 배포된 `/api/health` 호출
5. `/api/results` 요청 후 Storage Queue와 Application Insights 확인

## 확장 방향

이 샘플은 이후 Intune 장치 스크립트 결과 수집, Sentinel 인시던트 자동화, Purview 증거 처리 API로 확장할 수 있습니다.
