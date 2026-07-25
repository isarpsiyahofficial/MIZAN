from pathlib import Path
import sys

def main():
    root=Path(sys.argv[1]).resolve()
    p=root/'lib/screens/expenses_screen.dart'; t=p.read_text()
    if "import 'people_screen.dart';" not in t:
        t=t.replace("import '../widgets/mizan_cards.dart';", "import '../widgets/mizan_cards.dart';\nimport 'people_screen.dart';")
    t=t.replace("${shortDate(widget.day)} · ${weekdayLabel(widget.day)}", "${shortDate(widget.day)} · ${const ExpenseBrowserService().weekdayLabel(widget.day)}")
    t=t.replace('icon: recordIcon(item.type),','icon: _expensePaymentIcon(item.type),')
    start=t.index('  List<_ExpensePaymentDetail> _paymentDetails(')
    end=t.index('  Map<DateTime, List<_ExpensePaymentDetail>> _groupPayments', start)
    method='''  List<_ExpensePaymentDetail> _paymentDetails(
    MizanState state,
    DateTime? start,
    DateTime? end,
  ) {
    final result = <_ExpensePaymentDetail>[];
    bool included(DateTime value) =>
        (start == null || !dateOnly(value).isBefore(dateOnly(start))) &&
        (end == null || !dateOnly(value).isAfter(dateOnly(end)));
    for (final person in state.people) {
      for (final bank in person.banks) {
        for (final record in bank.products) {
          for (final payment in record.payments) {
            if (included(payment.paidAt)) {
              result.add(_ExpensePaymentDetail(
                person.id, person.name, RecordType.debt, record.id, bank.id,
                record.title, '${bank.userWrittenName} · ${record.displayKind}', payment,
              ));
            }
          }
        }
      }
      for (final record in person.personalDebts) {
        for (final payment in record.payments) {
          if (included(payment.paidAt)) {
            result.add(_ExpensePaymentDetail(person.id, person.name,
              RecordType.personalDebt, record.id, null, record.title,
              record.displayCreditor, payment));
          }
        }
      }
      for (final record in person.bills) {
        for (final payment in record.payments) {
          if (included(payment.paidAt)) {
            result.add(_ExpensePaymentDetail(person.id, person.name,
              RecordType.bill, record.id, null, record.kind.label,
              record.institutionName, payment));
          }
        }
      }
      for (final record in person.subscriptions) {
        for (final payment in record.payments) {
          if (included(payment.paidAt)) {
            result.add(_ExpensePaymentDetail(person.id, person.name,
              RecordType.subscription, record.id, null, record.title,
              record.providerName, payment));
          }
        }
      }
      for (final record in person.rents) {
        for (final payment in record.payments) {
          if (included(payment.paidAt)) {
            result.add(_ExpensePaymentDetail(person.id, person.name,
              RecordType.rent, record.id, null, record.title,
              record.receiverName, payment));
          }
        }
      }
    }
    result.sort((a, b) => b.payment.paidAt.compareTo(a.payment.paidAt));
    return result;
  }

'''
    t=t[:start]+method+t[end:]
    insert='''
IconData _expensePaymentIcon(RecordType type) => switch (type) {
  RecordType.debt => Icons.account_balance_outlined,
  RecordType.personalDebt => Icons.handshake_outlined,
  RecordType.bill => Icons.receipt_long_outlined,
  RecordType.subscription => Icons.autorenew_outlined,
  RecordType.rent => Icons.home_work_outlined,
};

'''
    idx=t.index('class _ExpensePaymentDetail')
    t=t[:idx]+insert+t[idx:]
    p.write_text(t)

    p=root/'lib/screens/people_screen.dart'; t=p.read_text()
    t=t.replace('icon: recordIcon(record.type),','icon: _personRecordIcon(record.type),')
    insert='''
IconData _personRecordIcon(RecordType type) => switch (type) {
  RecordType.debt => Icons.account_balance_outlined,
  RecordType.personalDebt => Icons.handshake_outlined,
  RecordType.bill => Icons.receipt_long_outlined,
  RecordType.subscription => Icons.autorenew_outlined,
  RecordType.rent => Icons.home_work_outlined,
};

'''
    idx=t.index('enum _PersonMetricMode')
    t=t[:idx]+insert+t[idx:]
    p.write_text(t)

    p=root/'lib/screens/reports_screen.dart'; t=p.read_text()
    t=t.replace(',\n    this.initiallyExpanded = false','')
    t=t.replace('  final bool initiallyExpanded;\n','')
    t=t.replace('      initiallyExpanded: initiallyExpanded,\n','')
    p.write_text(t)

    p=root/'test/csv_empty_merge_duplicate_test.dart'; t=p.read_text()
    t=t.replace('service.mergeStates(\n      current: MizanState.empty(),\n      imported: service.importState(service.exportState(imported)),\n    )','service.mergeStates(\n      MizanState.empty(),\n      service.importState(service.exportState(imported)),\n    )')
    p.write_text(t)
    print('Observation compile fixes applied.')
if __name__=='__main__': main()
