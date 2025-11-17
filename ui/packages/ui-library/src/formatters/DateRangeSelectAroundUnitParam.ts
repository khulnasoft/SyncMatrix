import { DateRangeSelectAroundUnit, isDateRangeSelectAroundUnit } from '@syncmatrix/design'
import { RouteParam, InvalidRouteParamValue } from '@syncmatrix/vue-compositions'
import { LocationQueryValue } from 'vue-router'

export class DateRangeSelectAroundUnitParam extends RouteParam<DateRangeSelectAroundUnit> {
  protected override parse(value: LocationQueryValue): DateRangeSelectAroundUnit {
    if (isDateRangeSelectAroundUnit(value)) {
      return value
    }

    throw new InvalidRouteParamValue()
  }

  protected override format(value: DateRangeSelectAroundUnit): LocationQueryValue {
    if (isDateRangeSelectAroundUnit(value)) {
      return value
    }

    throw new InvalidRouteParamValue()
  }
}