import pandas as pd

from checkyourdata.checks import get_implementation
from checkyourdata.schema import CheckConfig, CheckResult


class CheckRunner:
    def run(self, df: pd.DataFrame, checks: list[CheckConfig]) -> list[CheckResult]:
        results = []
        for check in checks:
            implementation = get_implementation(check.check_type)
            passed, details = implementation(df, check)
            results.append(CheckResult(check=check, passed=passed, details=details))
        return results
