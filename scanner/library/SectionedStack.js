class SectionedStack {
    constructor (sections) {
        this.__sections = sections
        this.__flat = {}
        this.__sectioned = {}
        this.__ordered_sections = []
    }
    add (section,value) {
        this.__flat[value] = true
        if (typeof this.__sectioned[section] === "undefined") {
            this.__sectioned[section] = []
            this.__ordered_sections.push(section)
        }
        this.__sectioned[section].push(value)
        
        // Removal
        const allSections = this.__ordered_sections
        if (allSections.length > this.__sections) {
            const sectionPopped = this.__ordered_sections.shift()
            for (const val of this.__sectioned[sectionPopped]) {
                delete this.__flat[val]
            }
            delete this.__sectioned[sectionPopped]
        }
    }
    exists(value) {
        return typeof this.__flat[value] !== "undefined"
    }
    sections () {
        return this.__ordered_sections
    }
    values () {
        return Object.keys(this.__flat)
    }
}
exports.SectionedStack = SectionedStack