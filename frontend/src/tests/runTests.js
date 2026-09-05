import { runAllTests } from './etaAndNearby.test.js';

runAllTests().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
