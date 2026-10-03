# Binary search: narrow the range

> English narration with Korean captions. The visual language keeps one array, one range, and one pointer across scenes.

## hook
A sorted array lets a search discard half its candidates at each comparison. [#sorted] The order is the reason this shortcut is safe.

## setup
This array has seven values. The first values are two and five. The next values are eight and twelve. The target value is sixteen. The last values are twenty three and thirty eight. [#target] We search for sixteen with zero based indexes.

## first
The current range runs from index zero to six. [#range] The middle index is floor of zero plus six divided by two, so it is three. The middle value is twelve. [#mid]

## found
Twelve is smaller than sixteen, so the left half cannot contain the target. [#discard-left] We keep indexes four through six. The middle is twenty three, which is too large, so we keep index four. [#discard-right] Index four contains sixteen. The search found it.

## missing
Now search for seven. [#missing] Twelve is larger, so we keep indexes zero through two. Five is smaller, so we keep index two. Eight is larger than seven, and the range becomes empty. [#empty] Seven is not in the array.

## bounds
A basic search stops at one match. [#bounds] A boundary search asks a different question. Lower bound finds the first value not less than the target. Upper bound finds the first value greater than the target.

## outro {hold=1.5}
Binary search works because order makes each comparison informative. [#summary] Check the sorted prerequisite before you discard a half.
