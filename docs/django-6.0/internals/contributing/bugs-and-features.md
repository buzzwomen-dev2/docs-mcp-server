# Reporting bugs and requesting features

#### IMPORTANT
Please report security issues **only** to
`security@djangoproject.com`. This is a private list only open to
long-time, highly trusted Django developers, and its archives are
not public. For further details, please see [our security
policies](../security.md).

<a id="reporting-bugs"></a>

## Reporting bugs

Before reporting a bug on the [ticket tracker](https://code.djangoproject.com/) consider these points:

* Check that someone hasn’t already filed the bug report by [searching](https://code.djangoproject.com/search) or
  running [custom queries](https://code.djangoproject.com/query) in the ticket tracker.
* Don’t use the ticket system to ask support questions. Use the [Django Forum](https://forum.djangoproject.com/)
  or the [Django Discord server](https://chat.djangoproject.com) for that.
* Don’t reopen issues that have been marked “wontfix” without finding consensus
  to do so on the [Django Forum](https://forum.djangoproject.com/).
* Don’t use the ticket tracker for lengthy discussions, because they’re
  likely to get lost. If a particular ticket is controversial, please move the
  discussion to the [Django Forum](https://forum.djangoproject.com/).

Well-written bug reports are *incredibly* helpful. However, there’s a certain
amount of overhead involved in working with any bug tracking system so your
help in keeping our ticket tracker as useful as possible is appreciated. In
particular:

* **Do** read the [FAQ](../../faq/index.md) to see if your issue might
  be a well-known question.
* **Do** ask on [Django Forum](https://forum.djangoproject.com/) or the [Django Discord server](https://chat.djangoproject.com) *first* if
  you’re not sure if what you’re seeing is a bug.
* **Do** write complete, reproducible, specific bug reports. You must
  include a clear, concise description of the problem, and a set of
  instructions for replicating it. Add as much debug information as you can:
  code snippets, test cases, exception backtraces, screenshots, etc. A nice
  small test case is the best way to report a bug, as it gives us a
  helpful way to confirm the bug quickly.
* **Don’t** post to [Django Forum](https://forum.djangoproject.com/) only to announce that you have filed a
  bug report. All the tickets are mailed to another list, [django-updates](../mailing-lists.md#django-updates-mailing-list),
  which is tracked by developers and interested community members; we see them
  as they are filed.

To understand the lifecycle of your ticket once you have created it, refer to
[Triage workflow](triaging-tickets.md#triage-workflow).

### Reporting user interface bugs

If your bug impacts anything visual in nature, there are a few additional
guidelines to follow:

* Include screenshots in your ticket which are the visual equivalent of a
  minimal test case. Show off the issue, not the crazy customizations
  you’ve made to your browser.
* If the issue is difficult to show off using a still image, consider
  capturing a *brief* screencast. If your software permits it, capture only
  the relevant area of the screen.
* If you’re offering a patch that changes the look or behavior of Django’s
  UI, you **must** attach before *and* after screenshots/screencasts.
  Tickets lacking these are difficult for triagers to assess quickly.
* Screenshots don’t absolve you of other good reporting practices. Make sure
  to include URLs, code snippets, and step-by-step instructions on how to
  reproduce the behavior visible in the screenshots.
* Make sure to set the UI/UX flag on the ticket so interested parties can
  find your ticket.
* If the issue relates to accessibility, please link to the relevant
  [accessibility standard](accessibility.md#accessibility-standards) if applicable.

<a id="requesting-features"></a>

## Requesting features

We’re always trying to make Django better, and your feature requests are a key
part of that. Here are some tips on how to make a request most effectively:

* Evaluate whether the feature idea requires changes in Django’s core. If your
  idea can be developed as an independent application or module — for
  instance, you want to support another database engine — we’ll probably
  suggest that you develop it independently. Then, if your project gathers
  sufficient community support, we may consider it for inclusion in Django.
* Propose the feature in the [new feature ideas](https://github.com/orgs/django/projects/24/) GitHub project (not in the
  ticket tracker) by creating a new item in the **Idea** column. This is where
  the community and the [Steering Council](../organization.md#steering-council) evaluate new
  ideas for the Django ecosystem. This step is especially important for large
  or complex proposals. We prefer to discuss any significant changes to
  Django’s core before any development begins. In some cases, a feature may be
  better suited as a third-party package, where it can evolve independently of
  Django’s release cycle.
* Describe clearly and concisely what the missing feature is and how you’d
  like to see it implemented. Include example code (non-functional is OK)
  if possible.
* Explain *why* you’d like the feature. Explaining a minimal use case will help
  others understand where it fits in, and if there are already other ways of
  achieving the same thing.

See also: [Documenting new features](writing-documentation.md#documenting-new-features).

## Requesting performance optimizations

Reports of a performance regression, or suggested performance optimizations,
should provide benchmarks and commands for the ticket triager to reproduce.

See the [django-asv benchmarks](writing-code/submitting-patches.md#django-asv-benchmarks) for more details of Django’s existing
benchmarks.

<a id="how-we-make-decisions"></a>

## How we make decisions

Whenever possible, we aim for rough consensus. Emoji reactions are used on
issues within the [new feature ideas](https://github.com/orgs/django/projects/24/) GitHub project to track community
feedback. The following meanings are assigned to each reaction:

* 👍: I support this feature and would use it
* 👎: I oppose this feature or believe it would cause issues for me or Django
* 😕: I have no strong opinion on this feature
* 🎉: This feature seems like a straightforward and beneficial addition

The [Steering Council](../organization.md#steering-council) will regularly review the ideas
in the project, moving those with community support through the following
stages:

* Idea
* Approved - Idea refinement - Team creation
* In progress
* Working solution - Review - Feedback
* Needs maintainer (Django only)
* Done

Occasionally, discussions on feature ideas or the direction of Django may take
place on the Django Forum. These discussions may include informal votes, which
follow the voting style invented by Apache and used on Python itself, where
votes are given as +1, +0, -0, or -1.
Roughly translated, these votes mean:

* +1: “I love the idea and I’m strongly committed to it.”
* +0: “Sounds OK to me.”
* -0: “I’m not thrilled, but I won’t stand in the way.”
* -1: “I strongly disagree and would be very unhappy to see the idea turn
  into reality.”

Although these votes are informal, they’ll be taken very seriously. After a
suitable voting period, if an obvious consensus arises we’ll follow the votes.
