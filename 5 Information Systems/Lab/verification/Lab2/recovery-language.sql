-- Localize only the explicitly created restart-test fixture; preserve status/timestamps/domain data.
UPDATE lab2_4101_import_operation
SET error_message = 'Предыдущий экземпляр завершился до фиксации операции'
WHERE id = 7 AND filename = 'restart-recovery-probe.json'
  AND status = 'FAILED' AND error_code = 'INTERRUPTED'
RETURNING id, status, error_code, error_message;
