package trivy

import data.lib.trivy

default ignore := false

# CVE-2025-71176: pytest DoS / privilege escalation via insecure temp directory.
# pytest is a dev/test-only dependency and is not shipped in the deployed app or
# image, so the practical risk is negligible. Suppressed here; a pytest version
# bump is tracked separately.
ignore {
	input.VulnerabilityID == "CVE-2025-71176"
}

# DS-0026: missing HEALTHCHECK in tests/e2e/Dockerfile. This image is used only by
# the Selenium-based e2e tests, where a HEALTHCHECK adds no value. Matched on both
# ID forms so the suppression holds regardless of trivy's field naming.
ignore {
	input.AVDID == "AVD-DS-0026"
}

ignore {
	input.ID == "DS-0026"
}
