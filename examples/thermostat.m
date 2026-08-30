#import <Foundation/OZObject.h>

@protocol Sensor
- (int)read;
@end

@interface Thermometer : OZObject <Sensor> {
        int _offset;
}
@property (nonatomic) int offset;
- (int)read;
@end

@implementation Thermometer

@synthesize offset = _offset;

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
        Thermometer *_probe;
        int _setpoint;
}
- (void)setProbe:(Thermometer *)probe;
- (BOOL)shouldHeat;
@end

@implementation Thermostat

- (void)setProbe:(Thermometer *)probe
{
        _probe = probe;
}

- (BOOL)shouldHeat
{
        return [_probe read] < _setpoint;
}

@end
