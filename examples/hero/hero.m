#import <Foundation/OZObject.h>
#import <Foundation/OZLog.h>

@interface Thermostat : OZObject {
        int _setpoint;
        BOOL _heating;
}
@property (atomic) int setpoint;
@property (nonatomic, getter=isHeating) BOOL heating;
@end

@implementation Thermostat

@synthesize setpoint = _setpoint;
@synthesize heating = _heating;

@end

int main(void)
{
        Thermostat *unit = [[Thermostat alloc] init];

        unit.setpoint = 21;
        unit.heating = [unit setpoint] > 18;

        OZLog("setpoint=%d heating=%d", [unit setpoint], [unit isHeating]);
        return 0;
}
