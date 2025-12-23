using Confluent.Kafka;
using Microsoft.AspNetCore.SignalR;

public class KafkaConsumerService : BackgroundService
{
    private readonly IHubContext<LogHub> _hubContext;
    private readonly string _topic = "system-logs";
    private readonly string _bootstrapServers = "127.0.0.1:9092";

    public KafkaConsumerService(IHubContext<LogHub> hubContext)
    {
        _hubContext = hubContext;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var config = new ConsumerConfig
        {
            BootstrapServers = _bootstrapServers,
            GroupId = "dashboard-group",
            AutoOffsetReset = AutoOffsetReset.Latest
        };

        using var consumer = new ConsumerBuilder<Ignore, string>(config).Build();
        consumer.Subscribe(_topic);

        Console.WriteLine("🟢 C# Dashboard: Listening to Kafka...");

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                var result = consumer.Consume(TimeSpan.FromMilliseconds(100));
                
                if (result != null)
                {
                    var logJson = result.Message.Value;
                    await _hubContext.Clients.All.SendAsync("ReceiveLog", logJson, stoppingToken);
                }
                
                await Task.Delay(100, stoppingToken);
            }
        }
        catch (OperationCanceledException)
        {
            consumer.Close();
        }
    }
}