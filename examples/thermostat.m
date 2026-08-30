/*
 * Demo source for objective-z.org. Everything in generated/ is oz_transpile's
 * own output for this file.
 */
#import <Foundation/OZObject.h>
#import <Foundation/OZTimer.h>

#include <zephyr/kernel.h>
#include <zephyr/zbus/zbus.h>

struct msg_setpoint {
        int celsius;
};

/* A Zephyr macro, used verbatim in an Objective-C file. No binding layer. */
ZBUS_CHAN_DEFINE(chan_setpoint, struct msg_setpoint, NULL, NULL,
                 ZBUS_OBSERVERS(lis_setpoint), ZBUS_MSG_INIT(0));

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
        OZTimer *_poll;
}
@property (atomic) int setpoint;
@property (nonatomic, getter=isHeating) BOOL heating;

- (instancetype)initWithProbe:(Thermometer *)probe pollEvery:(uint32_t)periodMs;
- (BOOL)shouldHeat;
@end

@implementation Thermostat

@synthesize setpoint = _setpoint;
@synthesize heating = _heating;

- (instancetype)initWithProbe:(Thermometer *)probe pollEvery:(uint32_t)periodMs
{
        _probe = probe;
        _poll = [[OZTimer alloc]
                initWithUserData:self
                          expiry:^(struct k_timer *t) {
                                  Thermostat *me =
                                          (__bridge Thermostat *)k_timer_user_data_get(t);
                                  [me setHeating:[me shouldHeat]];
                          }
                            stop:nil];
        [_poll startAfter:periodMs period:periodMs];
        return self;
}

- (BOOL)shouldHeat
{
        return [_probe read] < _setpoint;
}

@end

static Thermostat *unit;

/* A plain C callback that talks to the object. */
static void on_setpoint(const struct zbus_channel *chan)
{
        const struct msg_setpoint *msg = zbus_chan_const_msg(chan);

        [unit setSetpoint:msg->celsius];
}

ZBUS_LISTENER_DEFINE(lis_setpoint, on_setpoint);
