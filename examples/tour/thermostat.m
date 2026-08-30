/*
 * Demo source for objective-z.org. Everything under generated/ is
 * oz_transpile's own output for this file.
 */
#import <Foundation/Foundation.h>

#include <zephyr/kernel.h>
#include <zephyr/zbus/zbus.h>

@protocol Sensor
- (int)read;
@end

@interface Thermometer : OZObject <Sensor> {
        int _offset;
}
- (int)read;
@end

@implementation Thermometer

- (int)read
{
        return 21 + _offset;
}

@end

@interface Hygrometer : OZObject <Sensor> {
        int _humidity;
}
- (int)read;
@end

@implementation Hygrometer

- (int)read
{
        return _humidity;
}

@end

@interface Thermostat : OZObject {
        int _setpoint;
        BOOL _heating;
        Thermometer *_probe;
        OZArray *_bank;
        OZTimer *_poll;
}
@property (atomic) int setpoint;
@property (nonatomic, getter=isHeating) BOOL heating;

- (instancetype)initWithProbe:(Thermometer *)probe pollEvery:(uint32_t)periodMs;
- (int)worstReading;
- (int)spotCheck;
- (BOOL)shouldHeat;
@end

@implementation Thermostat

@synthesize setpoint = _setpoint;
@synthesize heating = _heating;

- (instancetype)initWithProbe:(Thermometer *)probe pollEvery:(uint32_t)periodMs
{
        _probe = probe;
        _bank = @[ probe, [[Hygrometer alloc] init] ];

        _poll = [[OZTimer alloc]
                initWithUserData:self
                expiry:^(struct k_timer *t) {
                        Thermostat *me = (__bridge Thermostat *)
                                k_timer_user_data_get(t);
                        [me setHeating:[me shouldHeat]];
                }
                stop:nil];
        [_poll startAfter:periodMs period:periodMs];
        return self;
}

- (int)worstReading
{
        int worst = 0;

        for (id sensor in _bank) {
                int value = [sensor read];

                if (value > worst) {
                        worst = value;
                }
        }

        return worst;
}

- (int)spotCheck
{
        Thermometer *spare = [[Thermometer alloc] init];
        int reading = [spare read];

        return reading;
}

- (BOOL)shouldHeat
{
        return [_probe read] < _setpoint;
}

@end

struct msg_setpoint {
        int celsius;
};

/* A Zephyr macro, used verbatim in an Objective-C file. No binding layer. */
ZBUS_CHAN_DEFINE(chan_setpoint, struct msg_setpoint, NULL, NULL,
                 ZBUS_OBSERVERS(lis_setpoint), ZBUS_MSG_INIT(0));

static Thermostat *unit;

/* A plain C callback that talks to the object. */
static void on_setpoint(const struct zbus_channel *chan)
{
        const struct msg_setpoint *msg = zbus_chan_const_msg(chan);

        [unit setSetpoint:msg->celsius];
}

ZBUS_LISTENER_DEFINE(lis_setpoint, on_setpoint);

int main(void)
{
        Thermometer *probe = [[Thermometer alloc] init];

        unit = [[Thermostat alloc] initWithProbe:probe pollEvery:1000];
        [unit setSetpoint:21];

        OZLog("worst=%d heating=%d", [unit worstReading], [unit isHeating]);
        return 0;
}
