import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class SingleWindowRateLimit implements RateLimit, Runnable {

  /** threshold */
  private final Integer limit;

  /** passed counter */
  private final AtomicInteger counter;

  /** duration */
  private final long duration;

  /** time unit type */
  private final TimeUnit timeUnit;

  /** background process thread */
  private ScheduledExecutorService scheduledExecutorService;

  /** 500 requests */
  private static final Integer DEFAULT_LIMIT_COUNT = 500;

  /** 1 second */
  private static final Integer DEFAULT_DURATION = 1000;

  /** Default constructor */
  public SingleWindowRateLimit() {
    this.limit = DEFAULT_LIMIT_COUNT;
    this.duration = DEFAULT_DURATION;
    this.timeUnit = TimeUnit.MILLISECONDS;
    counter = new AtomicInteger(0);
    this.startResetTask();
  }

  /**
   * Constructor with Configuration
   *
   * @param limit total limit
   * @param duration period
   * @param timeUnit time unit
   */
  public SingleWindowRateLimit(Integer limit, long duration, TimeUnit timeUnit) {
    this.limit = limit;
    this.duration = duration;
    this.timeUnit = timeUnit;
    counter = new AtomicInteger(0);
    this.startResetTask();
  }

  /**
   * Increment and check rate limit
   *
   * @return true = pass
   */
  @Override
  public boolean pass() {
    return counter.incrementAndGet() <= limit;
  }

  /** Inner async task for resetting the counter to 0 after duration */
  private void startResetTask() {
    scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();
    scheduledExecutorService.scheduleAtFixedRate(this, 0, duration, timeUnit);
  }

  /** Set counter to 0 */
  @Override
  public void run() {
    counter.set(0);
  }
}
